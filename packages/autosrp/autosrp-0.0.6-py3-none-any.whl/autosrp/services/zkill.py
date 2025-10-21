import logging
import time
import random
import datetime as dt
from typing import Iterable, Iterator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings

log = logging.getLogger(__name__)

BASE = "https://zkillboard.com/api"

def _ua() -> str:
    return getattr(settings, "AUTOSRP_USER_AGENT",
           getattr(settings, "AUTO_SRP_ZKILL_USER_AGENT", "aa-autosrp"))

def _headers() -> dict:
    return {"User-Agent": _ua(), "Accept": "application/json", "Accept-Encoding": "gzip"}

def get_session(timeout: int = 45) -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=7, connect=4, read=4,
        backoff_factor=0.7,
        status_forcelist=[429, 502, 503, 504, 520, 522, 524],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update(_headers())
    s.request_timeout = timeout  # type: ignore[attr-defined]
    return s

def month_spans_for(start: dt.datetime, end: dt.datetime) -> Iterator[tuple[int, int]]:
    y, m = start.year, start.month
    while (y < end.year) or (y == end.year and m <= end.month):
        yield (y, m)
        m += 1
        if m == 13:
            m, y = 1, y + 1

def url_for(kill_id: int) -> str:
    return f"https://zkillboard.com/kill/{kill_id}/"

def _get_json(session: requests.Session, url: str) -> list[dict]:
    try:
        r = session.get(url, timeout=getattr(session, "request_timeout", 45))
        if r.status_code != 200:
            log.debug("zKill HTTP %s for %s", r.status_code, url)
            return []
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        log.debug("zKill error %s for %s", e, url)
        return []

def fetch_losses_alliance_month(session: requests.Session, alliance_id: int, year: int, month: int, page: int) -> list[dict]:
    urls = (
        f"{BASE}/allianceID/{alliance_id}/losses/year/{year}/month/{month}/page/{page}/",
        f"{BASE}/losses/allianceID/{alliance_id}/year/{year}/month/{month}/page/{page}/",
    )
    for u in urls:
        rows = _get_json(session, u)
        if rows:
            return rows
    return []

def fetch_losses_corp_month(session: requests.Session, corp_id: int, year: int, month: int, page: int) -> list[dict]:
    urls = (
        f"{BASE}/corporationID/{corp_id}/losses/year/{year}/month/{month}/page/{page}/",
        f"{BASE}/losses/corporationID/{corp_id}/year/{year}/month/{month}/page/{page}/",
    )
    for u in urls:
        rows = _get_json(session, u)
        if rows:
            return rows
    return []

def fetch_losses_system_month(session: requests.Session, system_id: int, year: int, month: int, page: int) -> list[dict]:
    urls = (
        f"{BASE}/systemID/{system_id}/losses/year/{year}/month/{month}/page/{page}/",
        f"{BASE}/losses/systemID/{system_id}/year/{year}/month/{month}/page/{page}/",
        f"{BASE}/systemID/{system_id}/year/{year}/month/{month}/page/{page}/",
    )
    for u in urls:
        rows = _get_json(session, u)
        if rows:
            return rows
    return []

def enumerate_compact_by_orgs(session: requests.Session, start: dt.datetime, end: dt.datetime,
                              alliance_ids: Iterable[int], corp_ids: Iterable[int],
                              delay: float = 0.4) -> Iterator[tuple[int, str]]:
    seen: set[int] = set()
    for (Y, M) in month_spans_for(start, end):
        for aid in alliance_ids or []:
            page = 1
            while True:
                rows = fetch_losses_alliance_month(session, int(aid), Y, M, page)
                if not rows:
                    break
                for r in rows:
                    km = r.get("killmail_id")
                    h = (r.get("zkb") or {}).get("hash")
                    if not km or not h or km in seen:
                        continue
                    seen.add(km)
                    yield int(km), str(h)
                page += 1
                time.sleep(delay + random.random() * 0.3)
        for cid in corp_ids or []:
            page = 1
            while True:
                rows = fetch_losses_corp_month(session, int(cid), Y, M, page)
                if not rows:
                    break
                for r in rows:
                    km = r.get("killmail_id")
                    h = (r.get("zkb") or {}).get("hash")
                    if not km or not h or km in seen:
                        continue
                    seen.add(km)
                    yield int(km), str(h)
                page += 1
                time.sleep(delay + random.random() * 0.3)

def enumerate_compact_by_systems(session: requests.Session, start: dt.datetime, end: dt.datetime,
                                 system_ids: Iterable[int], delay: float = 0.4) -> Iterator[tuple[int, str]]:
    seen: set[int] = set()
    for (Y, M) in month_spans_for(start, end):
        for sid in system_ids or []:
            page = 1
            while True:
                rows = fetch_losses_system_month(session, int(sid), Y, M, page)
                if not rows:
                    break
                for r in rows:
                    km = r.get("killmail_id")
                    h = (r.get("zkb") or {}).get("hash")
                    if not km or not h or km in seen:
                        continue
                    seen.add(km)
                    yield int(km), str(h)
                page += 1
                time.sleep(delay + random.random() * 0.3)

def enumerate_compact_union(session: requests.Session, start: dt.datetime, end: dt.datetime,
                            system_ids: Iterable[int], alliance_ids: Iterable[int], corp_ids: Iterable[int],
                            delay: float = 0.4) -> Iterator[tuple[int, str]]:
    """Union of org- and system-based enumerations; de-duped by killmail_id."""
    yielded: set[int] = set()
    # orgs first (usually fewer pages), then systems
    for km_id, h in enumerate_compact_by_orgs(session, start, end, alliance_ids, corp_ids, delay):
        if km_id in yielded:
            continue
        yielded.add(km_id)
        yield km_id, h
    for km_id, h in enumerate_compact_by_systems(session, start, end, system_ids, delay):
        if km_id in yielded:
            continue
        yielded.add(km_id)
        yield km_id, h
