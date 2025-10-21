from decimal import Decimal
from typing import Dict, List, Tuple

from ..models import ItemPrices


def _get_price_map(type_ids: List[int], which: str = "sell") -> Dict[int, Decimal]:
    rows = ItemPrices.objects.filter(eve_type_id__in=type_ids).values("eve_type_id", which)
    return {r["eve_type_id"]: Decimal(str(r[which] or 0)) for r in rows}


def base_reward_for(doctrine_id: int, ship_type_id: int, app_settings, DoctrineRewardModel):
    rec = DoctrineRewardModel.objects.filter(doctrine_id=doctrine_id, ship_type_id=ship_type_id).first()
    if rec:
        return rec.base_reward_isk, (rec.penalty_scheme or (app_settings.default_penalty_scheme if app_settings else None))
    return Decimal("0.00"), (app_settings.default_penalty_scheme if app_settings else None)


def base_reward_for_fit(
    doctrine_id: int,
    ship_type_id: int,
    doctrine_fit_id: int | None,
    app_settings,
    DoctrineRewardModel,
):
    if doctrine_fit_id:
        fit_rec = DoctrineRewardModel.objects.filter(doctrine_fit_id=int(doctrine_fit_id)).first()
        if fit_rec:
            return fit_rec.base_reward_isk, (fit_rec.penalty_scheme or (app_settings.default_penalty_scheme if app_settings else None))
        return Decimal("0.00"), (app_settings.default_penalty_scheme if app_settings else None)

    return base_reward_for(doctrine_id, ship_type_id, app_settings, DoctrineRewardModel)


def hull_and_fit_prices(
    ship_type_id: int,
    fitted_type_ids: List[int] | dict,
    which: str = "sell"
) -> Tuple[Decimal, Decimal]:
    flat_ids: List[int] = []
    if isinstance(fitted_type_ids, dict):
        try:
            for k in ("high", "mid", "low", "rig", "sub"):
                flat_ids.extend(int(x) for x in (fitted_type_ids.get(k) or []))
        except Exception:
            flat_ids = []
    else:
        try:
            flat_ids = [int(x) for x in (fitted_type_ids or [])]
        except Exception:
            flat_ids = []

    ids = set(flat_ids or []) | {ship_type_id}
    price_map = _get_price_map(list(ids), which=which)
    hull = price_map.get(ship_type_id, Decimal("0"))
    fit = sum(price_map.get(t, Decimal("0")) for t in flat_ids)
    return hull, Decimal(fit)
