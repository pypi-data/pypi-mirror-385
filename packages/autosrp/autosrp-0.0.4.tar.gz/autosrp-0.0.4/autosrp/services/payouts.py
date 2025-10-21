from decimal import Decimal, ROUND_CEILING

from eveuniverse.models import EveType
from ..models import AppSetting, DoctrineReward, PayoutSuggestion, PenaltyScheme
from .penalties import compute_penalty_pct
from .pricing import hull_and_fit_prices, base_reward_for_fit

def _flatten_fitted_ids(fitted) -> list[int]:
    if not fitted:
        return []
    if isinstance(fitted, dict):
        out: list[int] = []
        for k in ("high", "mid", "low", "rig", "sub"):
            try:
                out.extend(int(x) for x in (fitted.get(k) or []))
            except Exception:
                continue
        return out
    try:
        return [int(x) for x in fitted]
    except Exception:
        return []


def _to_map(v):
    if not v:
        return {}
    if isinstance(v, dict):
        out = {}
        for k, q in v.items():
            try:
                tid = int(k)
                qty = int(q or 0) or 1
                out[tid] = out.get(tid, 0) + qty
            except Exception:
                continue
        return out
    if isinstance(v, (list, tuple, set)):
        out = {}
        for x in v:
            try:
                tid = int(x)
                out[tid] = out.get(tid, 0) + 1
            except Exception:
                continue
        return out
    try:
        return {int(v): 1}
    except Exception:
        return {}


def _cargo_ids_for_doctrine_fit(doctrine_fit_id: int) -> set[int]:
    try:
        from fittings.models import FittingItem
        rows = FittingItem.objects.filter(fit_id=doctrine_fit_id).values("flag", "type_id", "type_fk_id")
    except Exception:
        return set()
    FITTED_FLAGS = set(range(11, 35)) | set(range(92, 99)) | set(range(125, 133))
    cargo: set[int] = set()
    for it in rows:
        flag_val = it.get("flag")
        is_fitted = False
        if isinstance(flag_val, int):
            is_fitted = flag_val in FITTED_FLAGS
        else:
            sflag = str(flag_val or "").lower()
            if sflag.startswith(("hislot", "medslot", "loslot", "rigslot", "subsystem")):
                is_fitted = True
        if is_fitted:
            continue
        raw = it.get("type_id") or it.get("type_fk_id") or 0
        try:
            tid = int(raw)
        except Exception:
            tid = 0
        if tid:
            cargo.add(tid)
    return cargo


def compute_and_store_payout(kill, check):
    app = AppSetting.objects.filter(active=True).first()
    did = int(getattr(getattr(kill, "submission", None), "doctrine_id", 0) or 0)
    sid = int(getattr(kill, "ship_type_id", 0) or 0)
    fid = int(getattr(check, "doctrine_fit_id", 0) or 0) if check else None

    base_reward_isk, scheme = base_reward_for_fit(
        doctrine_id=did,
        ship_type_id=sid,
        doctrine_fit_id=fid,
        app_settings=app,
        DoctrineRewardModel=DoctrineReward,
    )

    has_check = bool(check)
    if has_check and isinstance(check, dict):
        check_payload = {
            "missing": check.get("missing") or [],
            "extra": check.get("extra") or [],
        }
        doctrine_fit_id = int(check.get("doctrine_fit_id") or 0)
    elif has_check:
        missing = getattr(check, "missing", []) or []
        extra = getattr(check, "extra", []) or []
        doctrine_fit_id = int(getattr(check, "doctrine_fit_id", 0) or 0)
        check_payload = {"missing": missing, "extra": extra}
    else:
        check_payload = {"missing": [], "extra": []}
        doctrine_fit_id = 0

    try:
        count_subs = bool(getattr(scheme, "count_subsystems", True)) if scheme else True
    except Exception:
        count_subs = True

    only_subs_discrepancies = False
    if has_check and not count_subs:
        try:
            miss_map = _to_map(check_payload.get("missing"))
            extra_map = _to_map(check_payload.get("extra"))

            ids = list(set(miss_map.keys()) | set(extra_map.keys()))
            cats = {}
            if ids:
                try:
                    cats = {
                        int(r["id"]): int(r["eve_group__eve_category_id"] or 0)
                        for r in EveType.objects.filter(id__in=ids).values("id", "eve_group__eve_category_id")
                    }
                except Exception:
                    cats = {}

            SUB_CAT = 32

            def _keep_non_sub(tid: int) -> bool:
                cat = int(cats.get(int(tid), -1))
                if cat == -1:
                    return False
                return cat != SUB_CAT

            miss_map_ns = {tid: q for tid, q in miss_map.items() if _keep_non_sub(int(tid))}
            extra_map_ns = {tid: q for tid, q in extra_map.items() if _keep_non_sub(int(tid))}

            only_subs_discrepancies = (len(miss_map_ns) == 0 and len(extra_map_ns) == 0) and (len(miss_map) + len(extra_map) > 0)
            check_payload = {"missing": miss_map_ns, "extra": extra_map_ns}
        except Exception:
            pass

    try:
        from autosrp.models import IgnoredModule
        ignored_ids = {int(x) for x in IgnoredModule.objects.values_list("eve_type_id", flat=True)}
        if ignored_ids:
            def _strip_ignored(val):
                if not val:
                    return val
                if isinstance(val, dict):
                    return {int(k): v for k, v in val.items() if int(k) not in ignored_ids}
                if isinstance(val, (list, tuple, set)):
                    out = []
                    for x in val:
                        try:
                            xi = int(x)
                        except Exception:
                            continue
                        if xi not in ignored_ids:
                            out.append(xi)
                    return out
                try:
                    return None if int(val) in ignored_ids else val
                except Exception:
                    return val
            check_payload["missing"] = _strip_ignored(check_payload.get("missing"))
            check_payload["extra"] = _strip_ignored(check_payload.get("extra"))
    except Exception:
        pass

    try:
        if scheme and bool(getattr(scheme, "relax_substitutions_no_penalty", False)) and doctrine_fit_id > 0:
            cargo_ids = _cargo_ids_for_doctrine_fit(doctrine_fit_id)
            if cargo_ids and check_payload.get("extra"):
                extra_map = _to_map(check_payload.get("extra"))
                extra_map_ns = {tid: q for tid, q in extra_map.items() if int(tid) not in cargo_ids}
                check_payload["extra"] = extra_map_ns
    except Exception:
        pass

    try:
        if doctrine_fit_id > 0:
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
            for it in FittingItem.objects.filter(fit_id=int(doctrine_fit_id)).values("flag", "quantity"):
                band = _band_for_flag(it.get("flag"))
                if band:
                    qty = int(it.get("quantity") or 0) or 1
                    d_bands[band] += qty

            a_bands = None
            ftids = getattr(kill, "fitted_type_ids", None)
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
                    if isinstance(check_payload.get("missing"), dict):
                        check_payload["missing"] = {}
                    else:
                        check_payload["missing"] = []
    except Exception:
        pass

    if (scheme is None) or (not has_check):
        penalty_pct, breakdown = Decimal("0.00"), {"wrong": 0, "capped": False}
    else:
        if (not count_subs) and only_subs_discrepancies:
            penalty_pct, breakdown = Decimal("0.00"), {"wrong": 0, "capped": False}
        else:
            penalty_pct, breakdown = compute_penalty_pct(check_payload, scheme)
            if penalty_pct == 0:
                def _count_items(val):
                    try:
                        if isinstance(val, list):
                            return len(val)
                        if isinstance(val, dict):
                            total = 0
                            for v in val.values():
                                if isinstance(v, list):
                                    total += len(v)
                                elif isinstance(v, dict):
                                    total += sum(int(x or 0) for x in v.values())
                                else:
                                    try:
                                        total += int(v)
                                    except Exception:
                                        total += 0
                            return total
                        return int(val)
                    except Exception:
                        return 0

                wrong_count = (_count_items(check_payload.get("missing")) + _count_items(check_payload.get("extra")))
                if wrong_count > 0:
                    per_wrong = getattr(scheme, "per_wrong_module_pct", Decimal("0.00")) or Decimal("0.00")
                    max_cap = getattr(scheme, "max_total_deduction_pct", Decimal("100.00")) or Decimal("100.00")
                    est = Decimal(wrong_count) * Decimal(per_wrong)
                    capped = est > max_cap
                    penalty_pct = min(est, max_cap).quantize(Decimal("0.01"))
                    breakdown = {"wrong": int(wrong_count), "capped": bool(capped)}

    fitted_flat = _flatten_fitted_ids(getattr(kill, "fitted_type_ids", []))

    hull_v, fit_v = hull_and_fit_prices(kill.ship_type_id, fitted_flat, which="sell")
    base = base_reward_isk or Decimal("0.00")

    valuation_basis = base if base > 0 else (hull_v + fit_v)
    suggested_base = (valuation_basis * (Decimal("100.00") - penalty_pct) / Decimal("100.00")).quantize(Decimal("0.01"))

    def _round_up_quarter_million(amount: Decimal) -> Decimal:
        if amount <= 0:
            return Decimal("0.00")
        INC = Decimal("250000")
        units = (amount / INC).to_integral_value(rounding=ROUND_CEILING)
        return (units * INC).quantize(Decimal("0.01"))

    suggested = _round_up_quarter_million(suggested_base)

    PayoutSuggestion.objects.update_or_create(
        kill=kill,
        defaults=dict(
            base_reward_isk=base,
            penalty_pct=penalty_pct,
            penalty_breakdown=breakdown,
            suggested_isk=suggested,
            hull_price_isk=hull_v,
            fit_price_isk=fit_v,
        ),
    )
