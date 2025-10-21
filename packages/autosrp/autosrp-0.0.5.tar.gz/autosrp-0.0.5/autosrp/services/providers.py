import logging
from datetime import datetime, timezone
import logging
from datetime import datetime, timezone
from typing import Optional

from esi.clients import EsiClientProvider

esi = EsiClientProvider()
log = logging.getLogger(__name__)


"""ESI killmail accessors"""
def get_killmail(killmail_id: int, killmail_hash: str) -> Optional[dict]:
    try:
        km_id = int(killmail_id)
        km_hash = str(killmail_hash)
        return esi.client.Killmails.get_killmails_killmail_id_killmail_hash(
            killmail_id=km_id,
            killmail_hash=km_hash
        ).result()
    except Exception as e:
        log.debug("ESI error %s for %s", e, killmail_id)
        return None


"""Killmail field helpers"""
def km_time(km: dict) -> datetime:
    v = (km or {}).get("killmail_time")
    if isinstance(v, datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    if isinstance(v, str):
        s = v.strip().replace(" ", "T").replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(s).astimezone(timezone.utc)
        except Exception:
            pass
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(str(v), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                continue
    raise TypeError(f"Unsupported killmail_time value: {type(v).__name__}={v!r}")


def km_system(km: dict) -> int:
    return int(km["solar_system_id"])


def km_victim(km: dict) -> dict:
    return km.get("victim") or {}


def _qty(item: dict) -> int:
    return int(item.get("quantity_destroyed", 0)) + int(item.get("quantity_dropped", 0)) or 1


def km_fitted_typeids(km: dict) -> list[int]:
    items = (km.get("victim") or {}).get("items") or []
    out: list[int] = []
    for it in items:
        tid_raw = it.get("item_type_id")
        if not tid_raw:
            continue
        try:
            tid = int(tid_raw)
        except (TypeError, ValueError):
            continue
        qty = _qty(it)
        out.extend([tid] * qty)
    return out
