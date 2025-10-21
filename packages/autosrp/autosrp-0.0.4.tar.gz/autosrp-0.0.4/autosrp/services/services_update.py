import logging
import requests
from celery import shared_task
from django.conf import settings
from django.db import Error
from django.utils import timezone as dj_timezone
from allianceauth.services.hooks import get_extension_logger

from ..models import ItemPrices

logger = get_extension_logger(__name__)

try:
    from eveuniverse.models import EveMarketPrice
except Exception:
    EveMarketPrice = None


"""External pricing API helpers"""
def valid_janice_api_key() -> bool:
    try:
        c = requests.get(
            "https://janice.e-351.com/api/rest/v2/markets",
            headers={
                "Content-Type": "text/plain",
                "X-ApiKey": getattr(settings, "AUTOSRP_JANICE_API_KEY", ""),
                "accept": "application/json",
            },
            timeout=20,
        ).json()
        if "status" in c:
            logger.info("Janice API status: %s", c)
            return False
        else:
            return True
    except Exception as e:
        logger.warning("Janice API check failed: %s", e)
        return False


def _update_price_bulk(type_ids):
    api_key = getattr(settings, "AUTOSRP_JANICE_API_KEY", "")
    if api_key:
        logger.info("Using Janice API for price updates")
        r = requests.post(
            "https://janice.e-351.com/api/rest/v2/pricer?market=2",
            data="\n".join([str(x) for x in type_ids]),
            headers={
                "Content-Type": "text/plain",
                "X-ApiKey": api_key,
                "accept": "application/json",
            },
            timeout=25,
        ).json()

        output = {}
        for item in r:
            output[str(item["itemType"]["eid"])] = {
                "buy": {
                    "max": str(item["immediatePrices"]["buyPrice5DayMedian"]),
                    "percentile": str(item["top5AveragePrices"]["buyPrice5DayMedian"]),
                },
                "sell": {
                    "min": str(item["immediatePrices"]["sellPrice5DayMedian"]),
                    "percentile": str(item["top5AveragePrices"]["sellPrice5DayMedian"]),
                },
            }
        return output
    else:
        logger.info("Using Fuzzworks API for price updates")
        return requests.get(
            "https://market.fuzzwork.co.uk/aggregates/",
            params={
                "types": ",".join([str(x) for x in type_ids]),
                "station": 60003760,
            },
            timeout=25,
        ).json()


"""Scheduled updates"""
@shared_task
def update_all_prices():
    type_ids = []
    market_data = {}

    prices = ItemPrices.objects.all()
    logger.info("Price update starting for %s items (Janice/Fuzzworks)...", len(prices))

    for item in prices:
        type_ids.append(item.eve_type_id)
        if len(type_ids) == 1000:
            market_data.update(_update_price_bulk(type_ids))
            type_ids.clear()

    if len(type_ids) > 0:
        market_data.update(_update_price_bulk(type_ids))

    logger.info("Market data fetched, starting database update...")
    missing_items = []
    for price in prices:
        key = str(price.eve_type_id)
        if key in market_data:
            buy = float(market_data[key]["buy"]["percentile"])
            sell = float(market_data[key]["sell"]["percentile"])
        else:
            missing_items.append(getattr(price.eve_type, "name", price.eve_type_id))
            buy, sell = 0, 0

        price.buy = buy
        price.sell = sell
        price.updated = dj_timezone.now()

    try:
        ItemPrices.objects.bulk_update(prices, ["buy", "sell", "updated"])
        logger.info("All prices successfully updated")
    except Error as e:
        logger.error("Error updating prices: %s", e)

    if EveMarketPrice:
        try:
            EveMarketPrice.objects.update_from_esi()
            logger.debug("Updated eveuniverse market prices.")
        except Exception as e:
            logger.warning("EveMarketPrice update_from_esi failed: %s", e)


@shared_task
def sync_itemprices_for_all_types(type_ids: list[int] | None = None):
    if not type_ids:
        logger.info("sync_itemprices_for_all_types: no type_ids provided; skipping.")
        return
    to_create = []
    existing = set(ItemPrices.objects.filter(eve_type_id__in=type_ids).values_list("eve_type_id", flat=True))
    for tid in type_ids:
        if tid not in existing:
            to_create.append(ItemPrices(eve_type_id=tid, buy=0, sell=0, updated=dj_timezone.now()))
    if to_create:
        ItemPrices.objects.bulk_create(to_create, ignore_conflicts=True)
        logger.info("Created %s ItemPrices rows.", len(to_create))
    else:
        logger.info("No missing ItemPrices rows.")
