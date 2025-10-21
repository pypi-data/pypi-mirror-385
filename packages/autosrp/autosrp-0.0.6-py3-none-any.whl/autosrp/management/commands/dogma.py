# Python
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

try:
    from eveuniverse.models import EveType
except Exception:
    EveType = None


META_LEVEL_ATTR_ID = 633       # metaLevel
META_GROUP_ID_ATTR_ID = 1692   # metaGroupID


def _safe_str(v):
    return "" if v is None else str(v)


def _get_attr_value(row):
    # EveUniverse typically keeps value on .value; fall back to common alternates
    for fld in ("value", "value_float", "value_int"):
        if hasattr(row, fld):
            val = getattr(row, fld, None)
            if val is not None:
                return val
    return None


class Command(BaseCommand):
    help = "Inspect Dogma data for one or more EVE type IDs. Usage: python manage.py dogma 4477 [--no-load] [--effects]"

    def add_arguments(self, parser):
        parser.add_argument(
            "type_ids",
            nargs="+",
            help="One or more EVE type IDs to inspect (e.g. 4477).",
        )
        parser.add_argument(
            "--no-load",
            action="store_true",
            dest="no_load",
            help="Do not attempt to load dogma data before inspecting.",
        )
        parser.add_argument(
            "--effects",
            action="store_true",
            dest="show_effects",
            help="Also list dogma effects for the type.",
        )

    def handle(self, *args, **options):
        if EveType is None:
            raise CommandError("eveuniverse is not available. Install/configure eveuniverse.")

        type_ids_raw = options["type_ids"]
        no_load = bool(options.get("no_load", False))
        show_effects = bool(options.get("show_effects", False))

        type_ids = []
        for v in type_ids_raw:
            try:
                type_ids.append(int(v))
            except (TypeError, ValueError):
                raise CommandError(f"Invalid type id: {v!r}")

        for tid in type_ids:
            self._process_type(tid, no_load, show_effects)

    def _ensure_dogma_loaded(self, type_id: int):
        try:
            call_command("eveuniverse_load_types autosrp", type_id_with_dogma=int(type_id))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"[warn] Loading dogma failed for {type_id}: {e}"))

    def _process_type(self, type_id: int, no_load: bool, show_effects: bool):
        if not no_load:
            self._ensure_dogma_loaded(type_id)

        t = EveType.objects.filter(id=int(type_id)).first()
        if not t:
            self.stdout.write(self.style.ERROR(f"[error] EveType {type_id} not found."))
            return

        # Basic info
        try:
            grp_id = getattr(t, "eve_group_id", None)
            grp_name = getattr(t.eve_group, "name", "") if getattr(t, "eve_group", None) else ""
        except Exception:
            grp_id, grp_name = None, ""

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING(f"EveType {t.id} – {t.name or ''}"))
        self.stdout.write(f"Group: id={_safe_str(grp_id)} name='{_safe_str(grp_name)}'")

        # Dogma attributes
        meta_level = None
        meta_group_id = None

        rel = getattr(t, "dogma_attributes", None)
        if rel is None:
            self.stdout.write(self.style.WARNING("[info] No dogma_attributes relation on EveType; try without --no-load."))
            return

        try:
            rows = list(rel.all().select_related("attribute"))
        except Exception:
            rows = list(rel.all())

        self.stdout.write("Dogma attributes:")
        if not rows:
            self.stdout.write("  (none)")
        else:
            for r in rows:
                try:
                    attr = getattr(r, "attribute", None)
                    attr_id = getattr(attr, "id", None)
                    attr_name = getattr(attr, "name", "") if attr else ""
                    val = _get_attr_value(r)

                    tag = ""
                    if attr_id == META_LEVEL_ATTR_ID or str(attr_name).lower() == "metalevel":
                        meta_level = val
                        tag = "  <= metaLevel (633)"
                    elif attr_id == META_GROUP_ID_ATTR_ID or str(attr_name).lower() == "metagroupid":
                        meta_group_id = val
                        tag = "  <= metaGroupID (1692)"

                    # Print without width/alignment specifiers to avoid formatting None
                    self.stdout.write(f"  - attr_id={_safe_str(attr_id)} name='{_safe_str(attr_name)}' value={_safe_str(val)}{tag}")
                except Exception as e:
                    self.stdout.write(f"  - [error reading attribute row]: {e}")

        if show_effects:
            self._print_effects(t)

        # Summary
        self.stdout.write("Summary:")
        self.stdout.write(f"  Group ID: {_safe_str(grp_id)}  Group Name: '{_safe_str(grp_name)}'")
        self.stdout.write(f"  Meta Level (attr 633): {_safe_str(meta_level)}")
        self.stdout.write(f"  Meta Group ID (attr 1692): {_safe_str(meta_group_id)}")

    def _print_effects(self, t):
        rel = getattr(t, "dogma_effects", None)
        self.stdout.write("Dogma effects:")
        if rel is None:
            self.stdout.write("  (relation missing)")
            return
        try:
            rows = list(rel.all())
        except Exception:
            rows = []
        if not rows:
            self.stdout.write("  (none)")
            return
        for e in rows:
            # Typical eveuniverse has id + name on the effect object
            eff_id = getattr(e, "id", None)
            eff_name = getattr(e, "name", "")
            self.stdout.write(f"  - effect_id={_safe_str(eff_id)} name='{_safe_str(eff_name)}'")
