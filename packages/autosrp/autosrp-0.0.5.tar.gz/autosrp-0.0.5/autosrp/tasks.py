import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from celery import shared_task
from django.utils import timezone as dj_timezone

from eveuniverse.models import EveType
from .models import Submission, KillRecord, AppSetting, FitCheck
from .services import zkill, fitcheck, payouts, providers

from .services.services_update import update_all_prices
import logging

log = logging.getLogger(__name__)


def _ensure_system_entities(system_ids: set[int]) -> None:
    try:
        from eveuniverse.models import EveEntity, EveSolarSystem
    except Exception:
        return
    if not system_ids:
        return
    try:
        existing = set(EveEntity.objects.filter(id__in=system_ids).values_list("id", flat=True))
        missing = [int(sid) for sid in system_ids if int(sid) not in existing]
        if not missing:
            return

        rows = {int(r["id"]): (r.get("name") or str(r["id"])) for r in EveSolarSystem.objects.filter(id__in=missing).values("id", "name")}
        to_create = []
        for sid in missing:
            name = rows.get(int(sid), str(sid))
            to_create.append(EveEntity(id=int(sid), name=name))
        if to_create:
            EveEntity.objects.bulk_create(to_create, ignore_conflicts=True)
    except Exception:
        pass


"""ESI fetch helpers using providers only"""
def _fetch_killmail_with_fallback(kill_id: int, kill_hash: str, timeout: int = 60) -> Optional[dict]:
    try:
        km = providers.get_killmail(int(kill_id), str(kill_hash))
        if km:
            return km
    except Exception as e:
        log.debug("ESI client error for %s: %s", kill_id, e)
    return None


"""Time window helpers"""
def _normalize_window(start: datetime, minutes: int) -> tuple[datetime, datetime]:
    s = start
    if s.tzinfo is None:
        s = s.replace(tzinfo=timezone.utc)
    s = s.astimezone(timezone.utc)
    e = s + timedelta(minutes=int(minutes or 0))
    return s, e


def _km_time_safe(km: dict) -> Optional[datetime]:
    v = (km or {}).get("killmail_time")
    try:
        if isinstance(v, str):
            s = v.strip().replace(" ", "T").replace("Z", "+00:00")
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
    return None


def _is_within(dt_val: datetime, start_utc: datetime, end_utc: datetime) -> bool:
    if dt_val.tzinfo is None:
        dt_val = dt_val.replace(tzinfo=timezone.utc)
    dt_val = dt_val.astimezone(timezone.utc)
    return (start_utc <= dt_val) and (dt_val < end_utc)


"""Banding helpers"""
def _flag_int(v):
    try:
        return int(str(v))
    except Exception:
        return None


def _bands_from_killmail(km: dict) -> dict[str, list[int]]:
    victim = (km or {}).get("victim") or {}
    items = victim.get("items") or []
    bands = {"high": [], "mid": [], "low": [], "rig": [], "sub": []}

    tmp: list[tuple[str, int]] = []
    for it in items:
        flag = _flag_int(it.get("flag", -1))
        tid = it.get("item_type_id")
        if flag is None or not tid:
            continue
        try:
            tid = int(tid)
        except Exception:
            continue
        if 27 <= flag <= 34:
            tmp.append(("high", tid))
        elif 19 <= flag <= 26:
            tmp.append(("mid", tid))
        elif 11 <= flag <= 18:
            tmp.append(("low", tid))
        elif 92 <= flag <= 98:
            tmp.append(("rig", tid))
        elif 125 <= flag <= 132:
            tmp.append(("sub", tid))

    try:
        type_ids = sorted({tid for _, tid in tmp})
        gmap = {
            int(r["id"]): (r.get("eve_group__name") or "")
            for r in EveType.objects.filter(id__in=type_ids).values("id", "eve_group__name")
        }
    except Exception:
        gmap = {}

    for band, tid in tmp:
        try:
            if (gmap.get(int(tid), "") or "").strip() == "Festival Launcher":
                continue
        except Exception:
            pass
        bands[band].append(int(tid))

    return bands


def _flatten_bands(fitted) -> list[int]:
    if isinstance(fitted, dict):
        out: list[int] = []
        for k in ("high", "mid", "low", "rig", "sub"):
            try:
                out.extend(int(x) for x in (fitted.get(k) or []))
            except Exception:
                continue
        return out
    try:
        return [int(x) for x in (fitted or [])]
    except Exception:
        return []


"""Main task"""
@shared_task(bind=True, autoretry_for=(), max_retries=0)
def process_submission(self, submission_id: int):
    sub = Submission.objects.get(id=submission_id)
    sub.status = "processing"
    sub.error = ""
    sub.save(update_fields=["status", "error"])

    try:
        app = AppSetting.objects.filter(active=True).first()
        ignore_capsules = bool(getattr(app, "ignore_capsules", True))
    except Exception:
        ignore_capsules = True

    start_utc, end_utc = _normalize_window(sub.start_at, sub.duration_minutes)
    raw_system_ids = list(sub.systems or [])
    try:
        system_id_set = {int(s) for s in raw_system_ids if s is not None}
    except Exception:
        system_id_set = {int(str(s)) for s in raw_system_ids if str(s).isdigit()}

    alliance_ids = list(getattr(sub.org_filter, "alliance_ids", []) or [])
    corp_ids = list(getattr(sub.org_filter, "corporation_ids", []) or [])
    alliance_set = {int(a) for a in alliance_ids if a is not None}
    corp_set = {int(c) for c in corp_ids if c is not None}

    zk_sess = zkill.get_session(timeout=60)
    pairs = zkill.enumerate_compact_union(
        zk_sess, start_utc, end_utc,
        system_ids=list(system_id_set), alliance_ids=alliance_ids, corp_ids=corp_ids, delay=0.45
    )

    ingested = 0
    skipped = 0
    failures = 0

    for kill_id, kill_hash in pairs:
        try:
            kill_id = int(kill_id)
            kill_hash = str(kill_hash or "")

            km = _fetch_killmail_with_fallback(kill_id, kill_hash, timeout=60)
            if not km:
                skipped += 1
                continue

            occurred = _km_time_safe(km)
            if occurred is None or not _is_within(occurred, start_utc, end_utc):
                skipped += 1
                continue

            try:
                km_system_id = int(providers.km_system(km))
            except Exception:
                km_system_id = int((km or {}).get("solar_system_id") or 0)

            if system_id_set and km_system_id not in system_id_set:
                skipped += 1
                continue

            victim = (km.get("victim") or {})
            ship_type_id = int(victim.get("ship_type_id") or 0)

            vic_alliance_id = victim.get("alliance_id")
            vic_corp_id = victim.get("corporation_id")
            try:
                vic_alliance_id = int(vic_alliance_id) if vic_alliance_id is not None else None
            except Exception:
                vic_alliance_id = None
            try:
                vic_corp_id = int(vic_corp_id) if vic_corp_id is not None else None
            except Exception:
                vic_corp_id = None

            if alliance_set or corp_set:
                allow = False
                if alliance_set and (vic_alliance_id is not None) and (vic_alliance_id in alliance_set):
                    allow = True
                if corp_set and (vic_corp_id is not None) and (vic_corp_id in corp_set):
                    allow = True
                if not allow:
                    skipped += 1
                    continue

            if ignore_capsules and ship_type_id:
                try:
                    row = EveType.objects.filter(id=ship_type_id).values("eve_group__name").first()
                    gname = ((row or {}).get("eve_group__name") or "").strip()
                    if gname.lower() == "capsule":
                        skipped += 1
                        continue
                except Exception:
                    pass

            bands = _bands_from_killmail(km)

            existing = KillRecord.objects.filter(killmail_id=kill_id).first()
            if existing and existing.submission_id != sub.id:
                skipped += 1
                continue

            if existing:
                kr = existing
                created = False
            else:
                kr, created = KillRecord.objects.get_or_create(
                    submission=sub,
                    killmail_id=kill_id,
                    defaults=dict(
                        killmail_hash=kill_hash,
                        zkb_url=f"https://zkillboard.com/kill/{kill_id}/",
                        occurred_at=occurred,
                        system_id=km_system_id,
                        victim_char_id=int(victim.get("character_id") or 0),
                        victim_corp_id=vic_corp_id or 0,
                        victim_alliance_id=vic_alliance_id,
                        ship_type_id=ship_type_id,
                        fitted_type_ids=bands,
                    ),
                )

            if not created:
                updates = {}
                if not kr.killmail_hash and kill_hash:
                    updates["killmail_hash"] = kill_hash
                if not kr.zkb_url:
                    updates["zkb_url"] = f"https://zkillboard.com/kill/{kill_id}/"
                if not kr.occurred_at:
                    updates["occurred_at"] = occurred
                if not kr.system_id:
                    updates["system_id"] = km_system_id
                if not kr.victim_char_id:
                    updates["victim_char_id"] = int(victim.get("character_id") or 0)
                if not kr.victim_corp_id:
                    updates["victim_corp_id"] = int(victim.get("corporation_id") or 0)
                if kr.victim_alliance_id is None and victim.get("alliance_id") is not None:
                    updates["victim_alliance_id"] = victim.get("alliance_id")
                if not kr.ship_type_id:
                    updates["ship_type_id"] = ship_type_id
                if not kr.fitted_type_ids:
                    updates["fitted_type_ids"] = bands
                if updates:
                    for k, v in updates.items():
                        setattr(kr, k, v)
                    kr.save(update_fields=list(updates.keys()))

            ids_for_compare = _flatten_bands(kr.fitted_type_ids)
            try:
                fc_result = fitcheck.compare(sub.doctrine_id, kr.ship_type_id, ids_for_compare, sub.strict_mode)
                dfid = fc_result["doctrine_fit_id"] or 0
                if hasattr(kr, "fitcheck"):
                    fc = kr.fitcheck
                    fc.doctrine_fit_id = dfid
                    fc.mode = fc_result.get("mode", getattr(fc, "mode", "strict"))
                    fc.passed = fc_result["passed"]
                    fc.missing = fc_result["missing"]
                    fc.extra = fc_result["extra"]
                    fc.substitutions = fc_result["substitutions"]
                    fc.notes = fc_result["notes"]
                    fc.save()
                else:
                    FitCheck.objects.create(
                        kill=kr,
                        doctrine_fit_id=dfid,
                        mode=fc_result.get("mode", "strict"),
                        passed=fc_result["passed"],
                        missing=fc_result["missing"],
                        extra=fc_result["extra"],
                        substitutions=fc_result["substitutions"],
                        notes=fc_result["notes"],
                    )
                payouts.compute_and_store_payout(kr, getattr(kr, "fitcheck", None))
                ingested += 1
            except Exception as e:
                failures += 1
                log.exception("fitcheck/payout failed for kill %s: %s", kill_id, e)
        except Exception as e:
            failures += 1
            log.exception("Error processing km %s: %s", kill_id, e)

    sub.status = "done"
    try:
        existing_sys = set()
        for s in list(sub.systems or []):
            try:
                existing_sys.add(int(s))
            except Exception:
                continue
        sys_from_kills = set(
            int(sid) for sid in
            KillRecord.objects.filter(submission=sub).values_list("system_id", flat=True)
            if sid is not None
        )
        merged = sorted(existing_sys | sys_from_kills)
        if merged != list(sub.systems or []):
            sub.systems = merged

        _ensure_system_entities(set(int(x) for x in merged))
    except Exception:
        pass

    sub.status = "done"
    sub.processed_at = dj_timezone.now()
    if failures > 0:
        sub.status = "done with errors"
        sub.error = f"Notes: ingested={ingested} skipped={skipped} failures={failures}"
    else:
        sub.error = ""
    if hasattr(sub, "systems"):
        sub.save(update_fields=["status", "processed_at", "error", "systems"])
    else:
        sub.save(update_fields=["status", "processed_at", "error"])
    return {"ingested": ingested, "skipped": skipped, "failures": failures}

@shared_task(bind=True, ignore_result=True)
def refresh_prices(self):
    log.info("Auto SRP: Starting scheduled price refresh…")
    update_all_prices.delay()

