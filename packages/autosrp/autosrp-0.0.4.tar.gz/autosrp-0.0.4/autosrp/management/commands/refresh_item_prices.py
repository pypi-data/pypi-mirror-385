from django.core.management.base import BaseCommand
from ...services.services_update import update_all_prices, sync_itemprices_for_all_types

from django.utils import timezone

try:
    from eveuniverse.models import EveType
except Exception:
    EveType = None

from ...models import ItemPrices

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    help = "Refresh ItemPrices using the canonical updater (services_update.update_all_prices)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sync",
            dest="run_async",
            action="store_false",
            help="Run synchronously in this process (wait until finished).",
        )
        parser.set_defaults(sync=False)

    def handle(self, *args, **options):

        sync: bool = bool(options.get("async"))
        if sync:
            logger.info("[INFO] Starting item sync via tasks…")
            sync_itemprices_for_all_types.delay()
            logger.info("[OK] Task queued: services_update.sync_itemprices_for_all_types")
        else:
            try:
                if EveType is None:
                    logger.warning("EveUniverse not available; skipping ItemPrices seed.")
                    return

                category_ids = [6, 7, 8, 11, 18, 20]
                now = timezone.now()

                type_ids = list(
                    EveType.objects.filter(eve_group__eve_category_id__in=category_ids).values_list("id", flat=True)
                )
                if not type_ids:
                    logger.warning("No EveType rows found for selected categories; skipping ItemPrices seed.")
                    return

                existing = set(
                    ItemPrices.objects.filter(eve_type_id__in=type_ids).values_list("eve_type_id", flat=True)
                )
                to_create = [ItemPrices(eve_type_id=int(tid), buy=0, sell=0, updated=now) for tid in type_ids if
                             int(tid) not in existing]
                if to_create:
                    ItemPrices.objects.bulk_create(to_create, ignore_conflicts=True)
                    logger.info(f"Seeded {len(to_create)} ItemPrices rows (buy/sell=0).")
                else:
                    logger.info("All ItemPrices rows already exist for selected categories.")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to seed ItemPrices: {e}"))

            logger.info("[INFO] Starting price refresh via tasks…")
            update_all_prices.delay()
            logger.info("[OK] Task queued: services_update.update_all_prices")
            return
