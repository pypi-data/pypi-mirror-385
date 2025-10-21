from decimal import Decimal
import csv
import re
from collections import Counter as _Counter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.views.generic import ListView, DetailView, View

from eveuniverse.models import EveEntity, EveType
from fittings.models import Fitting, FittingItem
from ..models import (
    Submission,
    KillRecord,
    PayoutRecord,
    AppSetting,
    FitCheck,
    DoctrineReward,
    PenaltyScheme,
)
from ..services import zkill as zks, providers, fitcheck, payouts, notifications, discord
from ..services.penalties import compute_penalty_pct


"""Batch list view"""
class BatchListView(PermissionRequiredMixin, ListView):
    permission_required = "autosrp.review"
    model = Submission
    template_name = "autosrp/review/batch_list.html"
    paginate_by = 50

    def get_queryset(self):
        return Submission.objects.order_by("-created")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        submissions = list(ctx.get("object_list", []))

        system_ids: set[int] = set()
        for s in submissions:
            try:
                for sid in (s.systems or []):
                    system_ids.add(int(sid))
            except Exception:
                continue

        names_map: dict[int, str] = {}
        try:
            rows = EveEntity.objects.filter(id__in=system_ids).values("id", "name")
            names_map = {int(r["id"]): r["name"] for r in rows}
        except Exception:
            names_map = {}

        for s in submissions:
            try:
                s.system_names = [names_map.get(int(sid), str(sid)) for sid in (s.systems or [])]
            except Exception:
                s.system_names = [str(x) for x in (s.systems or [])]

        doctrine_ids: set[int] = set(int(s.doctrine_id) for s in submissions if getattr(s, "doctrine_id", None))
        doctrine_map: dict[int, str] = {}
        try:
            from fittings.models import Doctrine
            rows = Doctrine.objects.filter(id__in=doctrine_ids).values("id", "name")
            doctrine_map = {int(r["id"]): r["name"] for r in rows}
        except Exception:
            doctrine_map = {}

        for s in submissions:
            try:
                did = int(s.doctrine_id) if s.doctrine_id is not None else None
                s.doctrine_name = doctrine_map.get(did, f"Doctrine {did}") if did is not None else ""
            except Exception:
                s.doctrine_name = "Error"

        for s in submissions:
            try:
                s.fit_mode_label = "Strict" if bool(getattr(s, "strict_mode", True)) else "Loose"
            except Exception:
                s.fit_mode_label = "Strict"

        return ctx


"""Batch detail view"""
class BatchDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "autosrp.review"
    model = Submission
    template_name = "autosrp/review/batch_detail.html"
    pk_url_kwarg = "submission_id"

    def get_object(self, queryset=None):
        return get_object_or_404(Submission, pk=self.kwargs.get(self.pk_url_kwarg))

    def _names_map(self, ids):
        ids = {int(x) for x in ids if x}
        if not ids:
            return {}
        rows = EveEntity.objects.filter(id__in=ids).values("id", "name")
        known = {int(r["id"]): r["name"] for r in rows}
        return known

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        submission = self.object
        ctx["submission"] = submission

        kills = submission.kills.all().order_by("occurred_at")

        try:
            for kr in kills:
                fc = getattr(kr, "fitcheck", None)
                if not fc or fc.passed:
                    continue

                doctrine_fit_id = int(getattr(fc, "doctrine_fit_id", 0) or 0)
                if doctrine_fit_id <= 0:
                    continue

                from fittings.models import FittingItem
                def _band_for_flag(flag_val) -> str | None:
                    if isinstance(flag_val, int):
                        f = int(flag_val)
                        if 27 <= f <= 34: return "high"
                        if 19 <= f <= 26: return "mid"
                        if 11 <= f <= 18: return "low"
                        if 92 <= f <= 98: return "rig"
                        return None
                    s = str(flag_val or "").lower()
                    if s.startswith("hislot"): return "high"
                    if s.startswith("medslot"): return "mid"
                    if s.startswith("loslot"): return "low"
                    if s.startswith("rigslot"): return "rig"
                    return None

                d_bands = {"high": 0, "mid": 0, "low": 0, "rig": 0}
                for it in FittingItem.objects.filter(fit_id=doctrine_fit_id).values("flag", "quantity"):
                    b = _band_for_flag(it.get("flag"))
                    if b:
                        d_bands[b] += int(it.get("quantity") or 0) or 1

                a_bands = None
                ftids = getattr(kr, "fitted_type_ids", None)
                if isinstance(ftids, dict):
                    a_bands = {
                        "high": len(ftids.get("high") or []),
                        "mid": len(ftids.get("mid") or []),
                        "low": len(ftids.get("low") or []),
                        "rig": len(ftids.get("rig") or []),
                    }

                if a_bands is not None:
                    has_shortfall = any(d_bands.get(b, 0) > a_bands.get(b, 0) for b in ("high", "mid", "low", "rig"))
                    if not has_shortfall:
                        km_payload = ftids if isinstance(ftids, dict) else []
                        fc_result = fitcheck.compare(submission.doctrine_id, kr.ship_type_id, km_payload, submission.strict_mode)
                        fc.doctrine_fit_id = int(fc_result.get("doctrine_fit_id") or 0)
                        fc.mode = fc_result.get("mode") or fc.mode
                        fc.passed = bool(fc_result.get("passed"))
                        fc.missing = fc_result.get("missing") or []
                        fc.extra = fc_result.get("extra") or []
                        fc.substitutions = fc_result.get("substitutions") or {}
                        fc.notes = fc_result.get("notes") or ""
                        fc.save()
        except Exception:
            pass

        ctx["kills"] = kills

        system_ids = set()
        char_ids = set()
        corp_ids = set()
        alli_ids = set()
        type_ids = set()
        for k in kills:
            if k.system_id:
                system_ids.add(int(k.system_id))
            if k.victim_char_id:
                try:
                    if int(k.victim_char_id) > 0:
                        char_ids.add(int(k.victim_char_id))
                except (TypeError, ValueError):
                    pass
            if k.victim_corp_id:
                corp_ids.add(int(k.victim_corp_id))
            if k.victim_alliance_id:
                alli_ids.add(int(k.victim_alliance_id))
            if k.ship_type_id:
                type_ids.add(int(k.ship_type_id))

        entity_ids = set().union(system_ids, char_ids, corp_ids, alli_ids)

        entity_names = self._names_map(entity_ids)
        type_names = {int(r["id"]): r["name"] for r in EveType.objects.filter(id__in=type_ids).values("id", "name")}

        for k in kills:
            k.system_name = entity_names.get(int(k.system_id), str(k.system_id)) if k.system_id else "Unknown"
            k.victim_char_name = entity_names.get(int(k.victim_char_id), "Unknown") if (k.victim_char_id or 0) > 0 else "Unknown"
            k.victim_corp_name = entity_names.get(int(k.victim_corp_id), str(k.victim_corp_id)) if k.victim_corp_id else "Unknown"
            k.victim_all_name = entity_names.get(int(k.victim_alliance_id), str(k.victim_alliance_id)) if k.victim_alliance_id else ""
            k.ship_type_name = type_names.get(int(k.ship_type_id), str(k.ship_type_id)) if k.ship_type_id else "Unknown"

        configured_sys_ids = list(submission.systems or [])
        if configured_sys_ids:
            sys_ids_for_title = [int(s) for s in configured_sys_ids]
        else:
            sys_ids_for_title = sorted({int(k.system_id) for k in kills if k.system_id})
        systems_list = []
        for sid in sys_ids_for_title:
            systems_list.append(entity_names.get(int(sid), str(sid)))
        ctx["systems_list"] = systems_list
        ctx["title_word"] = bool(systems_list)

        count = kills.count()
        passed = sum(1 for k in kills if hasattr(k, "fitcheck") and k.fitcheck.passed)
        failed = sum(1 for k in kills if hasattr(k, "fitcheck") and not k.fitcheck.passed)
        sum_suggested = sum((getattr(getattr(k, "payout", None), "final_isk", Decimal("0.00")) or Decimal("0.00")) for k in kills)
        ctx.update({"totals": {"count": count, "pass": passed, "fail": failed, "sum_suggested": sum_suggested}})

        fits_by_hull: dict[int, list[dict]] = {}
        doc_id = int(submission.doctrine_id)
        hull_ids = {int(k.ship_type_id) for k in kills if k.ship_type_id}
        for f in Fitting.objects.filter(doctrines__id=doc_id, ship_type_id__in=hull_ids).values("id", "name", "ship_type_id"):
            fits_by_hull.setdefault(int(f["ship_type_id"]), []).append({"id": int(f["id"]), "name": f["name"]})
        for k in kills:
            k.available_fits = fits_by_hull.get(int(k.ship_type_id or 0), [])

        for k in kills:
            pref_actual = None
            rec = getattr(k, "payout_record", None)
            if rec and rec.actual_isk:
                pref_actual = rec.actual_isk
            else:
                pref_actual = getattr(getattr(k, "payout", None), "suggested_isk", Decimal("0.00")) or Decimal("0.00")
            k.prefill_actual_isk = pref_actual

        return ctx


"""CSV export"""
class ExportToCsvView(PermissionRequiredMixin, View):
    permission_required = "autosrp.review"

    def post(self, request, submission_id: int):
        sub = get_object_or_404(Submission, pk=submission_id)
        ids = request.POST.getlist("kill_id")
        if ids:
            try:
                id_ints = [int(x) for x in ids]
            except ValueError:
                raise Http404("Invalid kill id.")
            kills = sub.kills.filter(id__in=id_ints).order_by("occurred_at")
        else:
            kills = sub.kills.all().order_by("occurred_at")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="autosrp_submission_{sub.id}.csv"'
        w = csv.writer(response)
        w.writerow(
            [
                "killmail_id",
                "zkb_url",
                "occurred_at_utc",
                "system_id",
                "victim_char_id",
                "victim_corp_id",
                "victim_alliance_id",
                "ship_type_id",
                "base_reward_isk",
                "penalty_pct",
                "suggested_isk",
                "hull_price_isk",
                "fit_price_isk",
                "override_isk",
                "final_isk",
                "fitcheck_passed",
                "fitcheck_missing",
                "fitcheck_extra",
            ]
        )

        for k in kills:
            payout = getattr(k, "payout", None)
            check = getattr(k, "fitcheck", None)
            w.writerow(
                [
                    k.killmail_id,
                    k.zkb_url,
                    k.occurred_at.isoformat(),
                    k.system_id,
                    k.victim_char_id,
                    k.victim_corp_id,
                    k.victim_alliance_id or "",
                    k.ship_type_id,
                    getattr(payout, "base_reward_isk", "") or "",
                    getattr(payout, "penalty_pct", "") or "",
                    getattr(payout, "suggested_isk", "") or "",
                    getattr(payout, "hull_price_isk", "") or "",
                    getattr(payout, "fit_price_isk", "") or "",
                    getattr(payout, "override_isk", "") or "",
                    getattr(payout, "final_isk", "") or "",
                    getattr(check, "passed", "") if check else "",
                    getattr(check, "missing", "") if check else "",
                    getattr(check, "extra", "") if check else "",
                ]
            )

        return response


"""Kill delete"""
class ReviewKillDeleteView(PermissionRequiredMixin, View):
    permission_required = "autosrp.review"

    def post(self, request, submission_id: int, kill_id: int):
        sub = get_object_or_404(Submission, pk=submission_id)
        kill = get_object_or_404(KillRecord, pk=kill_id, submission=sub)
        kill.delete()
        return redirect("autosrp:review_detail", submission_id=submission_id)


"""Add kill from zKill using providers ESI client"""
class ReviewKillAddFromZkillView(PermissionRequiredMixin, View):
    permission_required = "autosrp.review"
    ZK_RE = re.compile(r"https?://(?:beta\.)?zkillboard\.com/kill/(\d+)/?")

    def post(self, request, submission_id: int):
        submission = get_object_or_404(Submission, pk=submission_id)
        url = (request.POST.get("zkb_url") or "").strip()

        m = self.ZK_RE.match(url)
        if not m:
            messages.error(request, "Please paste a valid zKill URL like https://zkillboard.com/kill/12345678/")
            return redirect("autosrp:review_detail", submission_id=submission.id)

        killmail_id = int(m.group(1))

        sess = zks.get_session(timeout=60)
        zkill_url = f"{zks.BASE}/killID/{killmail_id}/"
        try:
            r = sess.get(zkill_url, timeout=getattr(sess, "request_timeout", 60))
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, list) or not data:
                messages.error(request, f"zKill returned no data for kill {killmail_id}.")
                return redirect("autosrp:review_detail", submission_id=submission.id)
            row = data[0]
            km_hash = (row.get("zkb") or {}).get("hash")
            if not km_hash:
                messages.error(request, f"zKill did not provide a hash for kill {killmail_id}.")
                return redirect("autosrp:review_detail", submission_id=submission.id)
        except Exception as e:
            messages.error(request, f"Error fetching kill from zKill: {e}")
            return redirect("autosrp:review_detail", submission_id=submission.id)

        # esi_sess = providers.get_session(timeout=60)
        #km = providers.get_killmail(killmail_id, km_hash, session=esi_sess)
        km = providers.get_killmail(killmail_id, km_hash)
        if not km:
            messages.error(request, f"ESI did not return details for kill {killmail_id}.")
            return redirect("autosrp:review_detail", submission_id=submission.id)

        occurred = providers.km_time(km)
        system_id = providers.km_system(km)
        victim = providers.km_victim(km)

        try:
            app = AppSetting.objects.filter(active=True).first()
            ignore_capsules = bool(getattr(app, "ignore_capsules", True))
        except Exception:
            ignore_capsules = True
        if ignore_capsules:
            try:
                ship_type_id_tmp = int(victim.get("ship_type_id") or 0)
                row = EveType.objects.filter(id=ship_type_id_tmp).values("eve_group__name").first()
                gname = ((row or {}).get("eve_group__name") or "").strip()
                if gname.lower() == "capsule":
                    messages.info(request, "Ignored capsule loss per admin settings.")
                    return redirect("autosrp:review_detail", submission_id=submission.id)
            except Exception:
                pass

        items = (victim or {}).get("items") or []

        def _flag_int(v):
            try:
                return int(str(v))
            except Exception:
                return None

        bands = {"high": [], "mid": [], "low": [], "rig": [], "sub": []}
        flag_map = []
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
                flag_map.append(("high", tid))
            elif 19 <= flag <= 26:
                flag_map.append(("mid", tid))
            elif 11 <= flag <= 18:
                flag_map.append(("low", tid))
            elif 92 <= flag <= 98:
                flag_map.append(("rig", tid))
            elif 125 <= flag <= 132:
                flag_map.append(("sub", tid))

        try:
            type_ids = sorted({tid for _, tid in flag_map})
            gmap = {
                int(r["id"]): (r.get("eve_group__name") or "")
                for r in EveType.objects.filter(id__in=type_ids).values("id", "eve_group__name")
            }
            for band, tid in flag_map:
                if (gmap.get(int(tid), "") or "").strip() == "Festival Launcher":
                    continue
                bands[band].append(int(tid))
        except Exception:
            for band, tid in flag_map:
                bands[band].append(int(tid))

        ship_type_id = int(victim.get("ship_type_id") or 0)
        existing = KillRecord.objects.filter(killmail_id=killmail_id).first()
        if existing and existing.submission_id != submission.id:
            messages.info(request, f"Kill {killmail_id} already exists in another submission; skipping.")
            return redirect("autosrp:review_detail", submission_id=submission.id)

        if existing:
            kr = existing
            created = False
        else:
            kr, created = KillRecord.objects.get_or_create(
                submission=submission,
                killmail_id=killmail_id,
                defaults=dict(
                    killmail_hash=km_hash,
                    zkb_url=f"https://zkillboard.com/kill/{killmail_id}/",
                    occurred_at=occurred,
                    system_id=system_id,
                    victim_char_id=int(victim.get("character_id") or 0),
                    victim_corp_id=int(victim.get("corporation_id") or 0),
                    victim_alliance_id=victim.get("alliance_id"),
                    ship_type_id=ship_type_id,
                    fitted_type_ids=bands,
                ),
            )

        if not created:
            updates = {}
            if not kr.killmail_hash and km_hash:
                updates["killmail_hash"] = km_hash
            if not kr.zkb_url:
                updates["zkb_url"] = f"https://zkillboard.com/kill/{killmail_id}/"
            if not kr.occurred_at:
                updates["occurred_at"] = occurred
            if not kr.system_id:
                updates["system_id"] = system_id
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

        flat_ids = []
        try:
            if isinstance(kr.fitted_type_ids, dict):
                for key in ("high", "mid", "low", "rig", "sub"):
                    flat_ids.extend(int(x) for x in (kr.fitted_type_ids.get(key) or []))
            else:
                flat_ids = [int(x) for x in (kr.fitted_type_ids or [])]
        except Exception:
            flat_ids = []

        try:
            km_payload = kr.fitted_type_ids if isinstance(kr.fitted_type_ids, dict) else flat_ids
            fc_result = fitcheck.compare(submission.doctrine_id, kr.ship_type_id, km_payload, submission.strict_mode)
            dfid = fc_result["doctrine_fit_id"] or 0

            if hasattr(kr, "fitcheck"):
                fc = kr.fitcheck
                fc.doctrine_fit_id = dfid
                fc.mode = fc_result["mode"]
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
                    mode=fc_result["mode"],
                    passed=fc_result["passed"],
                    missing=fc_result["missing"],
                    extra=fc_result["extra"],
                    substitutions=fc_result["substitutions"],
                    notes=fc_result["notes"],
                )
            payouts.compute_and_store_payout(kr, getattr(kr, "fitcheck", None))
        except Exception:
            pass

        messages.success(request, f"Added kill {killmail_id} to submission.")
        return redirect("autosrp:review_detail", submission_id=submission.id)


"""Utility helpers"""
def _slot_band(flag: int) -> str:
    if 27 <= flag <= 34:
        return "high"
    if 19 <= flag <= 26:
        return "mid"
    if 11 <= flag <= 18:
        return "low"
    if 92 <= flag <= 98:
        return "rig"
    if 125 <= flag <= 132:
        return "sub"
    return "other"


def _normalize_id_set(v) -> set[int]:
    if not v:
        return set()
    if isinstance(v, dict):
        try:
            return {int(k) for k in v.keys()}
        except Exception:
            return {int(x) for x in v.values() if isinstance(x, int) or (isinstance(x, str) and x.isdigit())}
    if isinstance(v, list):
        return {int(x) for x in v if isinstance(x, int) or (isinstance(x, str) and str(x).isdigit())}
    if isinstance(v, (int, str)):
        try:
            return {int(v)}
        except Exception:
            return set()
    return set()


def _normalize_id_qty_map(v) -> dict[int, int]:
    if not v:
        return {}

    out: dict[int, int] = {}
    try:
        if isinstance(v, dict):
            for k, q in v.items():
                try:
                    tid = int(k)
                    qty = int(q or 0)
                    if qty > 0:
                        out[tid] = out.get(tid, 0) + qty
                except Exception:
                    continue
        elif isinstance(v, list):
            for x in v:
                try:
                    tid = int(x)
                    out[tid] = out.get(tid, 0) + 1
                except Exception:
                    continue
        elif isinstance(v, (int, str)):
            tid = int(v)
            out[tid] = out.get(tid, 0) + 1
    except Exception:
        return {}

    return out


"""Kill fit detail modal"""
@require_GET
def kill_fit_detail(request, pk):
    try:
        kr = KillRecord.objects.select_related("fitcheck").get(pk=pk)
    except KillRecord.DoesNotExist:
        raise Http404("Kill not found")
    fc = getattr(kr, "fitcheck", None)

    def _normalize_id_list(v) -> list[int]:
        if not v:
            return []
        out: list[int] = []
        if isinstance(v, dict):
            band_keys = {"high", "mid", "low", "rig", "sub"}
            if any(k in v for k in band_keys):
                for k in ("high", "mid", "low", "rig", "sub"):
                    for x in (v.get(k) or []):
                        try:
                            out.append(int(x))
                        except Exception:
                            continue
                return out
            for k, q in v.items():
                try:
                    tid = int(k)
                    qty = int(q or 0) or 1
                    out.extend([tid] * qty)
                except Exception:
                    continue
            return out
        if isinstance(v, list):
            for x in v:
                try:
                    out.append(int(x))
                except Exception:
                    continue
            return out
        try:
            return [int(v)]
        except Exception:
            return []

    actual_ids: list[int] = _normalize_id_list(kr.fitted_type_ids)

    IGNORE_CATEGORY_IDS: set[int] = set(getattr(settings, "AUTOSRP_FITCHECK_IGNORE_CATEGORY_IDS", {8, 18, 20, 5}))
    ignored_tids_for_slots: set[int] = set()
    SUBSYSTEM_CATEGORY_ID = 32
    try:
        from autosrp.models import IgnoredModule as _IM
        ignored_tids_for_slots = {int(x) for x in _IM.objects.values_list("eve_type_id", flat=True)}
    except Exception:
        ignored_tids_for_slots = set()

    def _filter_ids_by_meta(ids_in: list[int]) -> list[int]:
        if not ids_in:
            return []
        dedup = sorted({int(t) for t in ids_in if t})
        rows = list(EveType.objects.filter(id__in=dedup).values("id", "eve_group__name", "eve_group__eve_category_id"))
        keep: set[int] = set()
        for r in rows:
            tid = int(r["id"])
            cat = int(r.get("eve_group__eve_category_id") or 0)
            if cat in IGNORE_CATEGORY_IDS:
                continue
            keep.add(tid)
        out: list[int] = []
        for t in ids_in:
            if int(t) in keep:
                out.append(int(t))
        return out

    actual_ids = _filter_ids_by_meta(actual_ids)

    from collections import Counter
    actual_counter: Counter = Counter(int(t) for t in actual_ids if t)

    doctrine_counter: Counter = Counter()
    doctrine_fit_id = int(getattr(fc, "doctrine_fit_id", 0) or 0)
    if doctrine_fit_id > 0:
        try:
            df = Fitting.objects.filter(id=doctrine_fit_id).first()
            if df:
                items = FittingItem.objects.filter(fit=df)

                def _safe_type_id(it) -> int | None:
                    for attr in ("type_id", "type_fk_id", "eve_type_id", "module_type_id"):
                        try:
                            v = getattr(it, attr, None)
                            if v:
                                return int(v)
                        except Exception:
                            continue
                    for fk in ("type", "type_fk", "eve_type", "module_type"):
                        try:
                            obj = getattr(it, fk, None)
                            if obj and getattr(obj, "id", None):
                                return int(obj.id)
                        except Exception:
                            continue
                    return None

                doc_raw_ids: list[int] = []
                for it in items:
                    tid_i = _safe_type_id(it)
                    if not tid_i:
                        continue
                    try:
                        qty = int(getattr(it, "quantity", None) or 0) or 1
                    except Exception:
                        qty = 1
                    if qty > 0:
                        doc_raw_ids.extend([int(tid_i)] * int(qty))

                doc_ids = _filter_ids_by_meta(doc_raw_ids)
                doctrine_counter = Counter(int(t) for t in doc_ids if t)
        except Exception:
            doctrine_counter = Counter()

    missing_map: dict[int, int] = {}
    extra_map: dict[int, int] = {}

    for tid, need in doctrine_counter.items():
        have = int(actual_counter.get(int(tid), 0))
        if have < need:
            missing_map[int(tid)] = need - have

    for tid, have in actual_counter.items():
        need = int(doctrine_counter.get(int(tid), 0))
        if have > need:
            extra_map[int(tid)] = have - need

    def _to_int_safe(x):
        try:
            return int(str(x))
        except Exception:
            return None

    def _iter_sub_pairs(subs_obj):
        if not subs_obj:
            return
        if isinstance(subs_obj, dict):
            for h, v in subs_obj.items():
                ek, av = _to_int_safe(h), _to_int_safe(v)
                if ek is not None and av is not None:
                    yield ek, av
            return
        if isinstance(subs_obj, (list, tuple, set)):
            for it in subs_obj:
                if isinstance(it, (list, tuple)) and len(it) == 2:
                    ek, av = _to_int_safe(it[0]), _to_int_safe(it[1])
                    if ek is not None and av is not None:
                        yield ek, av
                    continue
                if isinstance(it, dict):
                    for ek_key in ("expected", "from", "doctrine", "want", "required"):
                        for av_key in ("actual", "to", "fitted", "have", "used"):
                            if ek_key in it and av_key in it:
                                ek, av = _to_int_safe(it.get(ek_key)), _to_int_safe(it.get(av_key))
                                if ek is not None and av is not None:
                                    yield ek, av
                                break
            return

    subs_obj = getattr(fc, "substitutions", None) if fc else None

    for expected_id, actual_id in _iter_sub_pairs(subs_obj):
        if expected_id is None or actual_id is None:
            continue
        miss_q = int(missing_map.get(int(expected_id), 0))
        extra_q = int(extra_map.get(int(actual_id), 0))
        if miss_q > 0 and extra_q > 0:
            take = min(miss_q, extra_q)
            missing_map[int(expected_id)] = miss_q - take
            if missing_map.get(int(expected_id), 0) <= 0:
                if int(expected_id) in missing_map:
                    del missing_map[int(expected_id)]
            extra_map[int(actual_id)] = extra_q - take
            if extra_map.get(int(actual_id), 0) <= 0:
                if int(actual_id) in extra_map:
                    del extra_map[int(actual_id)]

    try:
        doctrine_band_counts: dict[str, int] = {"high": 0, "mid": 0, "low": 0, "rig": 0}
        actual_band_counts: dict[str, int] | None = None

        if doctrine_fit_id > 0:
            d_items = FittingItem.objects.filter(fit_id=doctrine_fit_id).values("flag", "quantity")
            for it in d_items:
                flag_val = it.get("flag")
                qty = int(it.get("quantity") or 0) or 1
                band = None
                if isinstance(flag_val, int):
                    band = _slot_band(flag_val)
                else:
                    s = str(flag_val or "").lower()
                    if s.startswith("hislot"):
                        band = "high"
                    elif s.startswith("medslot"):
                        band = "mid"
                    elif s.startswith("loslot"):
                        band = "low"
                    elif s.startswith("rigslot"):
                        band = "rig"
                    elif s.startswith("subsystem"):
                        band = "sub"
                if band in doctrine_band_counts:
                    doctrine_band_counts[band] += qty

        if isinstance(kr.fitted_type_ids, dict):
            actual_band_counts = {
                "high": len(kr.fitted_type_ids.get("high") or []),
                "mid": len(kr.fitted_type_ids.get("mid") or []),
                "low": len(kr.fitted_type_ids.get("low") or []),
                "rig": len(kr.fitted_type_ids.get("rig") or []),
            }

        if actual_band_counts is not None:
            bands_to_check = ("high", "mid", "low", "rig")
            has_shortfall = any(
                doctrine_band_counts.get(b, 0) > actual_band_counts.get(b, 0)
                for b in bands_to_check
            )
            if not has_shortfall:
                missing_map = {}
    except Exception:
        pass

    ref_ids_display = set(actual_counter.keys()) | set(missing_map.keys()) | set(extra_map.keys())
    names_map = {}
    group_meta: dict[int, tuple[str, int]] = {}
    if ref_ids_display:
        for r in EveType.objects.filter(id__in=list(ref_ids_display)).values("id", "name", "eve_group__name", "eve_group__eve_category_id"):
            names_map[int(r["id"])] = (r["name"] or f"Type {r['id']}")
            group_meta[int(r["id"])] = ((r.get("eve_group__name") or "").strip(), int(r.get("eve_group__eve_category_id") or 0))

    HI_EFFECT = 12
    MID_EFFECT = 13
    LOW_EFFECT = 11
    RIG_EFFECT = 2663
    SUB_EFFECT = 3772

    type_ids_for_banding = list(set(actual_counter.keys()))
    effects_by_type: dict[int, set[int]] = {}
    dogma_loaded = True
    dogma_error_detail = ""
    dogma_load_attempted = False
    dogma_missing_before = 0
    dogma_missing_after = 0

    try:
        if type_ids_for_banding:
            type_objs = list(EveType.objects.filter(id__in=type_ids_for_banding).prefetch_related("dogma_effects"))
            missing_dogma_ids: set[int] = set()
            for obj in type_objs:
                tid = int(obj.id)
                try:
                    eff_ids = set(int(e.id) for e in obj.dogma_effects.all())
                except Exception:
                    eff_ids = set()
                if not eff_ids:
                    missing_dogma_ids.add(tid)
                effects_by_type[tid] = eff_ids

            if missing_dogma_ids:
                from django.core.management import call_command
                try:
                    for tid in sorted(missing_dogma_ids):
                        call_command("eveuniverse_load_types", type_id_with_dogma=tid)
                except Exception as e:
                    dogma_loaded = False
                    dogma_error_detail = f"Dogma load command failed: {e}"

                try:
                    type_objs = list(EveType.objects.filter(id__in=type_ids_for_banding).prefetch_related("dogma_effects"))
                    effects_by_type = {}
                    still_missing = set()
                    for obj in type_objs:
                        tid = int(obj.id)
                        eff_ids = set(int(e.id) for e in obj.dogma_effects.all())
                        effects_by_type[tid] = eff_ids
                        if not eff_ids:
                            still_missing.add(tid)
                    if still_missing:
                        dogma_loaded = False
                        if not dogma_error_detail:
                            dogma_error_detail = f"Dogma still missing for type_ids: {sorted(still_missing)}"
                except Exception as e:
                    dogma_loaded = False
                    if not dogma_error_detail:
                        dogma_error_detail = f"Dogma re-fetch failed: {e}"

            if all((not v) for v in effects_by_type.values()):
                dogma_loaded = False
                if not dogma_error_detail:
                    dogma_error_detail = "No dogma effects found for involved types."
    except Exception as e:
        dogma_loaded = False
        dogma_error_detail = str(e)

    group_rows = {
        int(r["id"]): ((r.get("eve_group__name") or "").strip(), int(r.get("eve_group__eve_category_id") or 0))
        for r in EveType.objects.filter(id__in=type_ids_for_banding).values("id", "eve_group__name", "eve_group__eve_category_id")
    }

    def _band_for_tid(tid: int) -> str:
        effs = effects_by_type.get(int(tid), set())
        if effs:
            if SUB_EFFECT in effs:
                return "sub"
            if RIG_EFFECT in effs:
                return "rig"
            if HI_EFFECT in effs:
                return "high"
            if MID_EFFECT in effs:
                return "mid"
            if LOW_EFFECT in effs:
                return "low"
        gname, cat = group_rows.get(int(tid), ("", 0))
        if "Subsystem" in gname or cat == SUBSYSTEM_CATEGORY_ID:
            return "sub"
        if "Rig" in gname:
            return "rig"
        if cat == 7:
            return "high"
        return "other"

    extra_remaining: _Counter = _Counter(extra_map)
    allowed_sub_actual_ids = set()
    for _ek, _av in _iter_sub_pairs(subs_obj):
        if _av is not None:
            allowed_sub_actual_ids.add(int(_av))

    matched_actual_remaining: _Counter = _Counter()
    try:
        if fc and getattr(fc, "mode", "strict") == "loose":
            ref_ids_for_groups = set(actual_counter.keys()) | set(doctrine_counter.keys())
            grp_map_rows = {
                int(r["id"]): int(r.get("eve_group_id") or 0)
                for r in EveType.objects.filter(id__in=list(ref_ids_for_groups)).values("id", "eve_group_id")
            }
            from collections import Counter as Ctr
            need_by_group = Ctr(
                int(grp_map_rows.get(int(t), 0)) for t, q in doctrine_counter.items() for _ in range(int(q)))
            have_by_group = Ctr(
                int(grp_map_rows.get(int(t), 0)) for t, q in actual_counter.items() for _ in range(int(q)))

            from collections import defaultdict
            actual_tids_by_group = defaultdict(list)
            for tid, qty in actual_counter.items():
                gid = int(grp_map_rows.get(int(tid), 0))
                if gid > 0 and int(qty) > 0:
                    actual_tids_by_group[gid].append([int(tid), int(qty)])

            for gid, need_qty in list(need_by_group.items()):
                if gid <= 0:
                    continue
                matched = min(int(need_qty), int(have_by_group.get(gid, 0)))
                if matched <= 0:
                    continue
                bucket = actual_tids_by_group.get(gid, [])
                i = 0
                while matched > 0 and i < len(bucket):
                    tid_i, q_i = bucket[i]
                    take = min(matched, q_i)
                    if take > 0:
                        matched_actual_remaining[tid_i] += take
                        q_i -= take
                        matched -= take
                        bucket[i][1] = q_i
                    if q_i == 0:
                        i += 1
    except Exception:
        matched_actual_remaining = _Counter()

    def _status_for_tid(tid: int) -> tuple[str, str]:
        if int(tid) in ignored_tids_for_slots:
            return "ignored", "Ignored by admin"
        if fc and getattr(fc, "mode", "strict") == "loose":
            rem = int(matched_actual_remaining.get(int(tid), 0))
            if rem > 0:
                matched_actual_remaining[int(tid)] = rem - 1
                return "ok", "Group match (loose)"
        if int(tid) in allowed_sub_actual_ids:
            return "substitute", "Allowed substitution"
        if extra_remaining.get(int(tid), 0) > 0:
            extra_remaining[int(tid)] -= 1
            if extra_remaining[int(tid)] <= 0:
                del extra_remaining[int(tid)]
            return "extra", "Not in doctrine fit"
        return "ok", ""

    slots = {"high": [], "mid": [], "low": [], "rig": [], "sub": []}
    try:
        if isinstance(kr.fitted_type_ids, dict):
            _band_keys = ("high", "mid", "low", "rig", "sub")
            all_ids_in_bands: set[int] = set()
            for bk in _band_keys:
                for x in (kr.fitted_type_ids.get(bk) or []):
                    try:
                        all_ids_in_bands.add(int(x))
                    except Exception:
                        continue

            keep_ids: set[int] = set()
            meta_rows = {}
            if all_ids_in_bands:
                rows = list(EveType.objects.filter(id__in=all_ids_in_bands).values(
                    "id", "eve_group__name", "eve_group__eve_category_id"
                ))
                for r in rows:
                    tid_i = int(r["id"])
                    gname_i = (r.get("eve_group__name") or "").strip()
                    cat_i = int(r.get("eve_group__eve_category_id") or 0)
                    meta_rows[tid_i] = (gname_i, cat_i)
                    if (cat_i in IGNORE_CATEGORY_IDS) and (cat_i != SUBSYSTEM_CATEGORY_ID):
                        continue
                    keep_ids.add(tid_i)

            bands_src = {
                "high": [int(x) for x in (kr.fitted_type_ids.get("high") or []) if int(x) in keep_ids],
                "mid": [int(x) for x in (kr.fitted_type_ids.get("mid") or []) if int(x) in keep_ids],
                "low": [int(x) for x in (kr.fitted_type_ids.get("low") or []) if int(x) in keep_ids],
                "rig": [int(x) for x in (kr.fitted_type_ids.get("rig") or []) if int(x) in keep_ids],
                "sub": [int(x) for x in (kr.fitted_type_ids.get("sub") or []) if int(x) in keep_ids],
            }
        else:
            bands_src = {"high": [], "mid": [], "low": [], "rig": [], "sub": []}
            for tid, qty in actual_counter.items():
                b = _band_for_tid(int(tid))
                if b not in bands_src:
                    b = "high"
                for _ in range(int(qty)):
                    bands_src[b].append(int(tid))
        for band_name in ("high", "mid", "low", "rig", "sub"):
            for tid in bands_src.get(band_name, []):
                st, rsn = _status_for_tid(int(tid))
                slots[band_name].append({
                    "type_id": int(tid),
                    "name": names_map.get(int(tid), f"Type {tid}"),
                    "status": st,
                    "reason": rsn
                })
    except Exception as e:
        import logging, traceback
        logging.getLogger(__name__).exception("Dogma banding failed for kill_id=%s", getattr(kr, "killmail_id", None))
        tb = traceback.format_exc()
        detail = f"{e}\n\n{tb}" if getattr(settings, "DEBUG", False) else str(e)
        return HttpResponse(f"Error preparing slot bands: {detail}", status=500)

    if all(len(v) == 0 for v in slots.values()) and sum(actual_counter.values()) > 0:
        for tid, qty in actual_counter.items():
            for _ in range(int(qty)):
                st, rsn = _status_for_tid(int(tid))
                slots["high"].append({
                    "type_id": int(tid),
                    "name": names_map.get(int(tid), f"Type {tid}"),
                    "status": st,
                    "reason": rsn
                })

    name_map2 = {}
    ref_ids2 = set(missing_map.keys()) | set(extra_map.keys())
    if ref_ids2:
        name_map2 = {
            int(r["id"]): r["name"]
            for r in EveType.objects.filter(id__in=list(ref_ids2)).values("id", "name")
        }

    scheme: PenaltyScheme | None = None
    try:
        doc = DoctrineReward.objects.filter(
            doctrine_id=int(kr.submission.doctrine_id),
            ship_type_id=int(kr.ship_type_id),
        ).first()
        if doc and doc.penalty_scheme:
            scheme = doc.penalty_scheme
    except Exception:
        pass
    if scheme is None:
        try:
            scheme = PenaltyScheme.objects.filter(is_default=True).first()
        except Exception:
            pass

    per_missing_pct = getattr(scheme, "per_missing_module_pct", 0) or 0
    per_extra_pct = getattr(scheme, "per_extra_module_pct", 0) or 0

    missing_render = []
    for tid, qty in sorted(missing_map.items()):
        missing_render.append({
            "type_id": int(tid),
            "name": name_map2.get(int(tid), f"Type {tid}"),
            "qty": int(qty),
            "kind": "missing",
            "is_substitute": bool(tid in (getattr(fc, "substitutions", {}) or {}).keys()),
            "suggestion": name_map2.get(int(tid), f"Type {tid}"),
            "penalty_pct": per_missing_pct * int(qty) if per_missing_pct else 0,
        })
    for tid, qty in sorted(extra_map.items()):
        missing_render.append({
            "type_id": int(tid),
            "name": name_map2.get(int(tid), f"Type {tid}"),
            "qty": int(qty),
            "kind": "extra",
            "is_substitute": bool(tid in ((getattr(fc, "substitutions", {}) or {}).values())),
            "suggestion": "Remove or replace with doctrine module",
            "penalty_pct": per_extra_pct * int(qty) if per_extra_pct else 0,
        })

    try:
        if fc and getattr(fc, "mode", "strict") == "loose":
            penalty_total_pct, penalty_info = 0, {"wrong": 0, "capped": False}
            missing_render = []
        else:
            penalty_total_pct, penalty_info = compute_penalty_pct({"extra": extra_map, "missing": missing_map}, scheme)
    except Exception:
        penalty_total_pct, penalty_info = 0, {"wrong": 0, "capped": False}

    fit_title = ""
    try:
        row = EveType.objects.filter(id=kr.ship_type_id).values("name").first()
        ship_name = (row or {}).get("name") or ""
        if ship_name:
            fit_title = ship_name
    except Exception:
        fit_title = ""

    payout = getattr(kr, "payout", None)
    payout_record = getattr(kr, "payout_record", None)

    payout_base = getattr(payout, "base_reward_isk", Decimal("0.00")) or Decimal("0.00")
    payout_penalty_pct = getattr(payout, "penalty_pct", Decimal("0.00")) or Decimal("0.00")
    payout_suggested = getattr(payout, "suggested_isk", Decimal("0.00")) or Decimal("0.00")
    hull_price_isk = getattr(payout, "hull_price_isk", Decimal("0.00")) or Decimal("0.00")
    fit_price_isk = getattr(payout, "fit_price_isk", Decimal("0.00")) or Decimal("0.00")
    payout_override = getattr(payout, "override_isk", None)
    payout_final = payout_override if payout_override is not None else payout_suggested
    payout_actual = getattr(payout_record, "actual_isk", None)

    try:
        html = render_to_string(
            "autosrp/review/_kill_fit_detail.html",
            context={
                "kill": kr,
                "fitcheck": fc,
                "slots": slots,
                "missing_ids": sorted(set(missing_map.keys())),
                "missing_items": missing_render,
                "missing_render": missing_render,
                "mode": getattr(fc, "mode", "strict") if fc else "strict",
                "ship_type_id": kr.ship_type_id,
                "doctrine_fit_id": getattr(fc, "doctrine_fit_id", None),
                "fit_title": fit_title,
                "penalty_scheme_name": getattr(scheme, "name", "") if scheme else "",
                "penalty_total_pct": penalty_total_pct,
                "penalty_capped": bool(penalty_info.get("capped", False)),
                "penalty_wrong_count": int(penalty_info.get("wrong", 0)),
                "kill_comment": getattr(kr, "status_comment", "") or "",
                "fitcheck_notes": getattr(fc, "notes", "") if fc else "",
                "hull_price_isk": hull_price_isk,
                "fit_price_isk": fit_price_isk,
                "loss_total_isk": (hull_price_isk or Decimal("0")) + (fit_price_isk or Decimal("0")),
                "payout_base": payout_base,
                "payout_penalty_pct": payout_penalty_pct,
                "payout_penalty_isk": None,
                "payout_suggested": payout_suggested,
                "payout_override": payout_override,
                "payout_final": payout_final,
                "payout_actual": payout_actual,
                "dogma_loaded": dogma_loaded,
                "dogma_error": dogma_error_detail,
                "dogma_load_attempted": dogma_load_attempted,
                "dogma_missing_before": dogma_missing_before,
                "dogma_missing_after": dogma_missing_after,
                "fitcheck_effective_passed": (sum(missing_map.values()) + sum(extra_map.values())) == 0,
            },
            request=request,
        )
        return HttpResponse(html)
    except Exception as e:
        import logging, traceback
        logging.getLogger(__name__).exception(
            "Error rendering kill_fit_detail for kill_id=%s (submission_id=%s)",
            getattr(kr, "killmail_id", None),
            getattr(getattr(kr, "submission", None), "id", None),
        )
        tb = traceback.format_exc()
        detail = f"{e}\n\n{tb}" if getattr(settings, "DEBUG", False) else str(e)
        return HttpResponse(f"Error rendering fit detail: {detail}", status=500)


"""Re-run fitcheck"""
class RerunFitCheckView(PermissionRequiredMixin, View):
    permission_required = "autosrp.review"

    def post(self, request, submission_id: int):
        sub = get_object_or_404(Submission, pk=submission_id)
        kills = list(sub.kills.all().select_related("fitcheck"))

        changed = 0
        for kr in kills:
            if isinstance(kr.fitted_type_ids, dict):
                ids_for_compare = kr.fitted_type_ids
            else:
                ids_for_compare = [int(x) for x in (kr.fitted_type_ids or [])]

            forced_raw = (request.POST.get(f"fit_for_{kr.id}") or "").strip()

            try:
                forced_id = int(forced_raw) if forced_raw else None
            except (TypeError, ValueError):
                forced_id = None

            if forced_id:
                fc_result = fitcheck.compare_with_fit(forced_id, kr.ship_type_id, ids_for_compare, sub.strict_mode)
            else:
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
            changed += 1

        messages.success(request, f"Re-ran fit checks for {changed} kills.")
        return redirect("autosrp:review_detail", submission_id=submission_id)


"""Save payouts"""
class SavePayoutsView(PermissionRequiredMixin, View):
    permission_required = "autosrp.review"

    def post(self, request, submission_id: int):
        sub = get_object_or_404(Submission, pk=submission_id)
        kills = list(sub.kills.all())
        saved = 0

        for kr in kills:
            actual_raw = (request.POST.get(f"actual_for_{kr.id}") or "").strip()
            if actual_raw == "":
                continue
            try:
                actual = Decimal(actual_raw)
            except Exception:
                continue

            suggested = getattr(getattr(kr, "payout", None), "suggested_isk", Decimal("0.00")) or Decimal("0.00")
            system_name = ""
            try:
                if kr.system_id:
                    ent = EveEntity.objects.filter(id=int(kr.system_id)).values("name").first()
                    system_name = (ent or {}).get("name") or ""
            except Exception:
                system_name = ""

            PayoutRecord.objects.update_or_create(
                kill=kr,
                defaults=dict(
                    suggested_isk=suggested,
                    actual_isk=actual,
                    system_id=kr.system_id or 0,
                    system_name=system_name,
                ),
            )
            saved += 1

        messages.success(request, f"Saved actual payouts for {saved} kills.")
        return redirect("autosrp:review_detail", submission_id=submission_id)


"""Save kill status and notify"""
@method_decorator(csrf_protect, name="dispatch")
class SaveKillStatusView(PermissionRequiredMixin, View):
    permission_required = "autosrp.review"

    def post(self, request, submission_id: int, kill_id: int):
        target = get_object_or_404(KillRecord, pk=kill_id, submission_id=submission_id)

        action = (request.POST.get("action") or "").strip()
        comment = (request.POST.get("comment") or "").strip()

        if action not in {"approve", "comment", "reject"}:
            return HttpResponseBadRequest("Invalid action provided.")

        if action in {"comment", "reject"} and not comment:
            messages.error(request, "A comment/reason is required for this action.")
            return redirect("autosrp:review_detail", submission_id=submission_id)

        if action == "approve":
            target.status = "approved"
            target.status_comment = ""
        elif action == "comment":
            target.status = "approved_with_comment"
            target.status_comment = comment
        elif action == "reject":
            target.status = "rejected"
            target.status_comment = comment

        target.reviewer = self.request.user
        target.reviewed_at = timezone.now()

        target.save(update_fields=["status", "status_comment", "reviewer", "reviewed_at"])

        if action == "reject":
            try:
                existing_rec = getattr(target, "payout_record", None)
                existing_suggested = getattr(existing_rec, "suggested_isk", None)
                fallback_suggested = getattr(getattr(target, "payout", None), "final_isk", Decimal("0.00")) or Decimal("0.00")
                suggested_to_store = existing_suggested if existing_suggested is not None else fallback_suggested

                system_name = ""
                try:
                    if target.system_id:
                        ent = EveEntity.objects.filter(id=int(target.system_id)).values("name").first()
                        system_name = (ent or {}).get("name") or ""
                except Exception:
                    system_name = ""

                PayoutRecord.objects.update_or_create(
                    kill=target,
                    defaults=dict(
                        suggested_isk=suggested_to_store,
                        actual_isk=Decimal("0.00"),
                        system_id=target.system_id or 0,
                        system_name=system_name,
                    ),
                )
            except Exception:
                pass
        else:
            try:
                actual_raw = (request.POST.get(f"actual_for_{target.id}") or "").strip()
                if actual_raw != "":
                    try:
                        actual_val = Decimal(actual_raw)
                    except Exception:
                        actual_val = None

                    if actual_val is not None:
                        existing_rec = getattr(target, "payout_record", None)
                        existing_suggested = getattr(existing_rec, "suggested_isk", None)
                        fallback_suggested = getattr(getattr(target, "payout", None), "final_isk", Decimal("0.00")) or Decimal("0.00")
                        suggested_to_store = existing_suggested if existing_suggested is not None else fallback_suggested

                        system_name = ""
                        try:
                            if target.system_id:
                                ent = EveEntity.objects.filter(id=int(target.system_id)).values("name").first()
                                system_name = (ent or {}).get("name") or ""
                        except Exception:
                            system_name = ""

                        PayoutRecord.objects.update_or_create(
                            kill=target,
                            defaults=dict(
                                suggested_isk=suggested_to_store,
                                actual_isk=actual_val,
                                system_id=target.system_id or 0,
                                system_name=system_name,
                            ),
                        )
            except Exception:
                pass

        vic_char_id = int(target.victim_char_id or 0)
        requester_user = None
        if vic_char_id <= 0:
            messages.info(request, "No victim character ID on this kill; skipping notification.")
        else:
            try:
                from allianceauth.authentication.models import CharacterOwnership
                co = (
                    CharacterOwnership.objects
                    .select_related("user", "character")
                    .filter(character__character_id=vic_char_id)
                    .first()
                )
                requester_user = getattr(co, "user", None) if co else None
            except Exception as e:
                messages.error(request, f"Could not resolve owner via CharacterOwnership: {e}")

            if requester_user is None:
                try:
                    from allianceauth.eveonline.models import EveCharacter
                    from ..services.users import get_user_for_character
                    eve_char = EveCharacter.objects.filter(character_id=vic_char_id).first()
                    if eve_char:
                        requester_user = get_user_for_character(eve_char)
                except Exception as e:
                    messages.error(request, f"Could not resolve owner via EveCharacter: {e}")

            if requester_user is None:
                messages.info(request, f"No owning user found for victim_char_id={vic_char_id}; skipping notification.")
            else:
                status_to_level = {
                    "approved": "success",
                    "approved_with_comment": "info",
                    "rejected": "danger",
                    "submitted": "info",
                }
                level = status_to_level.get(target.status, "info")

                try:
                    notifications.notify_requester(
                        requester=requester_user,
                        srp_request=target,
                        message_level=level,
                    )
                except Exception as e:
                    messages.error(request, f"Notification send failed: {e}")

        messages.success(request, f"Kill {target.killmail_id} marked as '{action}'.")
        return redirect("autosrp:review_detail", submission_id=submission_id)

"""Toggle submission strict/loose mode and re-run fitcheck (manager only)"""
class ToggleFitModeView(PermissionRequiredMixin, View):
    permission_required = "autosrp.manage"

    def post(self, request, submission_id: int):
        sub = get_object_or_404(Submission, pk=submission_id)
        new_mode = not bool(getattr(sub, "strict_mode", True))
        sub.strict_mode = new_mode
        try:
            sub.save(update_fields=["strict_mode"])
        except Exception:
            sub.save()


        messages.info(request, f"Fit check mode switched to {'Loose' if not new_mode else 'Strict'}. Re-running fit checks…")
        return RerunFitCheckView.as_view()(request, submission_id=submission_id)
