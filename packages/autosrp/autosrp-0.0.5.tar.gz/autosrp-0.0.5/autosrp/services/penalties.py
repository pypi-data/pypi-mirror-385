from decimal import Decimal


"""Helpers"""
def _sumq(values) -> int:
    try:
        return sum(int(x.get("qty", 1)) if isinstance(x, dict) else 1 for x in (values or []))
    except Exception:
        return len(list(values or []))


def _flatten_banded(val):
    """Normalize penalty inputs that may come as banded dicts:
       {"high":[...], "mid":[...], "low":[...], "rig":[...], "sub":[...]}
       Returns a flat list of type_ids. If val is already a list/map/other, returns it unchanged.
    """
    if not isinstance(val, dict):
        return val
    bands = ("high", "mid", "low", "rig", "sub")
    if any(k in val for k in bands):
        flat = []
        for k in bands:
            items = val.get(k) or []
            try:
                flat.extend(int(x) for x in items)
            except Exception:
                flat.extend([x for x in items if isinstance(x, int)])
        return flat


"""Penalty computation"""
def compute_penalty_pct(check, scheme) -> tuple[Decimal, dict]:
    missing = extra = None
    if isinstance(check, dict):
        missing = check.get("missing")
        extra = check.get("extra")
    elif check is not None:
        try:
            missing = getattr(check, "missing", None)
            extra = getattr(check, "extra", None)
        except Exception:
            missing = extra = None

    missing = _flatten_banded(missing)
    extra = _flatten_banded(extra)

    wrong = _sumq(missing) + _sumq(extra)

    def _qty_total(v) -> int:
        if not v:
            return 0
        if isinstance(v, (list, tuple, set)):
            if v and isinstance(next(iter(v), None), (list, dict, tuple, set)):
                return sum(_qty_total(x) for x in v)
            return len(v)
        if isinstance(v, dict):
            total = 0
            for _, val in v.items():
                if isinstance(val, (list, dict, tuple, set)):
                    total += _qty_total(val)
                    continue
                try:
                    q = int(val)
                except Exception:
                    q = 1
                if q > 0:
                    total += q
            if total == 0 and v:
                total = len(v.keys())
            return total
        try:
            return int(v)
        except Exception:
            return 0

    miss_qty = _qty_total(missing)
    extra_qty = _qty_total(extra)
    wrong_total = miss_qty + extra_qty

    per_wrong = getattr(scheme, "per_wrong_module_pct", Decimal("0.00")) or Decimal("0.00")
    per_miss = getattr(scheme, "per_missing_module_pct", None)
    per_extra = getattr(scheme, "per_extra_module_pct", None)

    miss_rate = (per_miss if per_miss not in (None, 0) else per_wrong) or Decimal("0.00")
    extra_rate = (per_extra if per_extra not in (None, 0) else per_wrong) or Decimal("0.00")

    pct = (Decimal(miss_qty) * Decimal(miss_rate)) + (Decimal(extra_qty) * Decimal(extra_rate))
    capped = False
    max_cap = getattr(scheme, "max_total_deduction_pct", None)
    if max_cap is not None and pct > max_cap:
        pct = max_cap
        capped = True

    return pct, {"wrong": wrong_total, "capped": capped}
