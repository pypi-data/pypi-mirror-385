from datetime import timedelta
from decimal import Decimal
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count, F, DecimalField, Q, ExpressionWrapper, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from autosrp.forms import DiscordSettingsForm
from autosrp.models import DiscordNotificationSetting, Submission, KillRecord, PayoutSuggestion, PayoutRecord

try:
    from allianceauth.authentication.models import CharacterOwnership
except Exception:
    CharacterOwnership = None

try:
    from eveuniverse.models import EveEntity, EveType
except Exception:
    EveEntity = None
    EveType = None

try:
    from fittings.models import Doctrine
except Exception:
    Doctrine = None


"""Helpers"""
def _fmt_isk(v):
    try:
        val = Decimal(v)
        return f"{val:,.2f}"
    except Exception:
        return "-"


def _get_user_srp_requests(user, limit=50):
    """
    Return a list of dicts for the user's SRP-eligible KillRecords enriched with:
      - victim character name
      - ship name
      - doctrine name
      - payout label + amount
      - status text + bootstrap color class
      - link targets for zKill and modal fit detail
    """
    try:
        if CharacterOwnership is None:
            raise RuntimeError("CharacterOwnership unavailable")
        char_ids = [
            int(cid)
            for cid in CharacterOwnership.objects.filter(user=user).values_list("character__character_id", flat=True)
            if cid is not None
        ]
    except Exception:
        char_ids = []

    if not char_ids:
        return []

    try:
        qs = (
            KillRecord.objects
            .select_related("submission")
            .filter(victim_char_id__in=char_ids)
            .order_by("-occurred_at", "-id")[:limit]
        )
        rows = list(qs)
    except Exception:
        return []

    if not rows:
        return []

    vic_ids = sorted({int(r.victim_char_id) for r in rows if getattr(r, "victim_char_id", None)})
    char_name_map = {}
    try:
        if EveEntity is None:
            raise RuntimeError("EveEntity unavailable")
        char_name_map = {
            int(r["id"]): (r["name"] or f"Character {r['id']}")
            for r in EveEntity.objects.filter(id__in=vic_ids).values("id", "name")
        }
    except Exception:
        char_name_map = {}

    type_ids = sorted({int(r.ship_type_id) for r in rows if getattr(r, "ship_type_id", None)})
    ship_name_map = {}
    try:
        if EveType is None:
            raise RuntimeError("EveType unavailable")
        ship_name_map = {
            int(r["id"]): (r["name"] or f"Type {r['id']}")
            for r in EveType.objects.filter(id__in=type_ids).values("id", "name")
        }
    except Exception:
        ship_name_map = {}

    doctrine_ids = sorted({
        int(getattr(getattr(r, "submission", None), "doctrine_id", 0))
        for r in rows if getattr(getattr(r, "submission", None), "doctrine_id", None)
    })
    doctrine_name_map = {}
    try:
        if Doctrine is None:
            raise RuntimeError("Doctrine unavailable")
        doctrine_name_map = {
            int(r["id"]): (r["name"] or f"Doctrine {r['id']}")
            for r in Doctrine.objects.filter(id__in=doctrine_ids).values("id", "name")
        }
    except Exception:
        doctrine_name_map = {did: f"Doctrine {did}" for did in doctrine_ids}

    def _status_class(s: str) -> str:
        s = (s or "").lower()
        if s == "approved":
            return "text-success"
        if s == "approved_with_comment":
            return "text-primary"
        if s == "rejected":
            return "text-danger"
        return "text-muted"

    out = []
    for r in rows:
        char_name = char_name_map.get(int(getattr(r, "victim_char_id", 0)) or 0, str(getattr(r, "victim_char_id", "-")))
        ship_name = ship_name_map.get(int(getattr(r, "ship_type_id", 0)) or 0, str(getattr(r, "ship_type_id", "-")))
        doctrine_id = int(getattr(getattr(r, "submission", None), "doctrine_id", 0) or 0)
        doctrine_name = doctrine_name_map.get(doctrine_id, f"Doctrine {doctrine_id}" if doctrine_id else "")

        payout = getattr(r, "payout", None)
        payout_record = getattr(r, "payout_record", None)

        actual_val = getattr(payout_record, "actual_isk", None)
        final_val = getattr(payout, "final_isk", None)

        status = getattr(r, "status", "submitted")
        status_lower = (status or "").lower()

        if actual_val is not None:
            value_label = "Actual payout"
            value_amount = _fmt_isk(actual_val)
        else:
            if status_lower in {"approved", "approved_with_comment"}:
                value_label = "Payout"
                value_amount = _fmt_isk(final_val) if final_val is not None else "-"
            else:
                value_label = "Potential payout"
                value_amount = _fmt_isk(final_val) if final_val is not None else "-"

        out.append(
            {
                "id": int(getattr(r, "id", 0)),
                "occurred_at": getattr(r, "occurred_at", None),
                "char_name": char_name,
                "ship_name": ship_name,
                "doctrine_name": doctrine_name,
                "killmail_id": int(getattr(r, "killmail_id", 0) or 0),
                "zkb_url": getattr(r, "zkb_url", "") or (f"https://zkillboard.com/kill/{getattr(r, 'killmail_id', 0)}/" if getattr(r, "killmail_id", None) else ""),
                "status": status,
                "status_class": _status_class(status),
                "status_modal_url": reverse("autosrp:kill-fit-detail", kwargs={"pk": int(getattr(r, "id", 0))}),
                "value_label": value_label,
                "value_amount": value_amount,
                "comment": getattr(r, "status_comment", "") or "",
            }
        )

    return out


"""View"""
@login_required
def user_landing(request):
    setting, _ = DiscordNotificationSetting.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = DiscordSettingsForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            return redirect(reverse("autosrp:user_landing"))
    else:
        form = DiscordSettingsForm(instance=setting)

    my_srp_requests = _get_user_srp_requests(request.user, limit=50)

    user = request.user

    try:
        if CharacterOwnership is None:
            raise RuntimeError("CharacterOwnership unavailable")
        owned_char_ids = list(
            CharacterOwnership.objects.filter(user=user)
            .values_list("character__character_id", flat=True)
        )
        owned_char_ids = [int(cid) for cid in owned_char_ids if cid is not None]
    except Exception:
        owned_char_ids = []

    if owned_char_ids:
        user_kills = KillRecord.objects.filter(victim_char_id__in=owned_char_ids)

        total_requests = user_kills.count()

        total_fights = user_kills.values("submission_id").distinct().count()

        loss_value_expr = ExpressionWrapper(
            F("hull_price_isk") + F("fit_price_isk"),
            output_field=DecimalField(max_digits=20, decimal_places=2),
        )
        total_loss = (
            PayoutSuggestion.objects.filter(kill__victim_char_id__in=owned_char_ids)
            .annotate(loss_value=loss_value_expr)
            .aggregate(
                total=Coalesce(
                    Sum("loss_value"),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=20, decimal_places=2)),
                )
            )
            .get("total")
        )

        total_paid = (
            PayoutRecord.objects.filter(kill__victim_char_id__in=owned_char_ids)
            .aggregate(
                total=Coalesce(
                    Sum("actual_isk"),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=20, decimal_places=2)),
                )
            )
            .get("total")
        )

        avg_requests_per_fight = (total_requests / total_fights) if total_fights else 0
        avg_loss_per_fight = (total_loss / total_fights) if total_fights else 0
        avg_paid_per_fight = (total_paid / total_fights) if total_fights else 0

        avg_suggested_per_request = (
            PayoutSuggestion.objects.filter(kill__victim_char_id__in=owned_char_ids)
            .aggregate(
                v=Coalesce(
                    Avg("suggested_isk"),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=20, decimal_places=2)),
                )
            )
            .get("v")
        )

        avg_final_per_request = (
            PayoutSuggestion.objects.filter(kill__victim_char_id__in=owned_char_ids)
            .annotate(
                final_isk=Coalesce(
                    F("override_isk"),
                    F("suggested_isk"),
                    output_field=DecimalField(max_digits=20, decimal_places=2),
                )
            )
            .aggregate(
                v=Coalesce(
                    Avg("final_isk"),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=20, decimal_places=2)),
                )
            )
            .get("v")
        )

        submitted_cnt = user_kills.filter(status="submitted").count()
        approved_cnt = user_kills.filter(status="approved").count()
        approved_with_comment_cnt = user_kills.filter(status="approved_with_comment").count()
        rejected_cnt = user_kills.filter(status="rejected").count()

        avg_penalty_pct = (
            PayoutSuggestion.objects.filter(kill__victim_char_id__in=owned_char_ids)
            .aggregate(
                v=Coalesce(
                    Avg("penalty_pct"),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=5, decimal_places=2)),
                )
            )
            .get("v")
        )
        now = timezone.now()
        start_month = (now.replace(day=1) - timedelta(days=180)).replace(day=1)

        def ym(dt):
            return dt.strftime("%Y-%m")

        labels = []
        cursor = start_month
        for _ in range(7):
            labels.append(ym(cursor))
            if cursor.month == 12:
                cursor = cursor.replace(year=cursor.year + 1, month=1)
            else:
                cursor = cursor.replace(month=cursor.month + 1)

        kills_qs = (
            user_kills.filter(occurred_at__gte=start_month)
            .annotate(m=TruncMonth("occurred_at"))
            .values("m")
            .annotate(c=Count("id"))
            .order_by("m")
        )
        kills_map = {ym(r["m"]): r["c"] for r in kills_qs}
        kills_per_month = [kills_map.get(label, 0) for label in labels]

        paid_qs = (
            PayoutRecord.objects.filter(kill__victim_char_id__in=owned_char_ids, kill__occurred_at__gte=start_month)
            .annotate(m=TruncMonth("kill__occurred_at"))
            .values("m")
            .annotate(
                s=Coalesce(
                    Sum("actual_isk"),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=20, decimal_places=2)),
                )
            )
            .order_by("m")
        )
        paid_map = {ym(r["m"]): float(r["s"]) for r in paid_qs}
        paid_per_month = [paid_map.get(label, 0.0) for label in labels]

        loss_qs = (
            PayoutSuggestion.objects.filter(kill__victim_char_id__in=owned_char_ids, kill__occurred_at__gte=start_month)
            .annotate(m=TruncMonth("kill__occurred_at"), loss_value=loss_value_expr)
            .values("m")
            .annotate(
                s=Coalesce(
                    Sum("loss_value"),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=20, decimal_places=2)),
                )
            )
            .order_by("m")
        )
        loss_map = {ym(r["m"]): float(r["s"]) for r in loss_qs}
        loss_per_month = [loss_map.get(label, 0.0) for label in labels]
    else:
        total_requests = 0
        total_fights = 0
        total_loss = Decimal("0.00")
        total_paid = Decimal("0.00")
        avg_requests_per_fight = 0
        avg_loss_per_fight = 0
        avg_paid_per_fight = 0
        avg_suggested_per_request = Decimal("0.00")
        avg_final_per_request = Decimal("0.00")
        submitted_cnt = approved_cnt = approved_with_comment_cnt = rejected_cnt = 0
        avg_penalty_pct = Decimal("0.00")
        labels = []
        kills_per_month = []
        paid_per_month = []
        loss_per_month = []

    user_stats_ctx = {
        "u_total_loss": total_loss,
        "u_total_paid": total_paid,
        "u_total_fights": total_fights,
        "u_total_kills": total_requests,
        "u_avg_kills_per_fight": avg_requests_per_fight,
        "u_avg_loss_per_fight": avg_loss_per_fight,
        "u_avg_paid_per_fight": avg_paid_per_fight,
        "u_avg_suggested_per_kill": avg_suggested_per_request,
        "u_avg_final_per_kill": avg_final_per_request,
        "u_submitted_cnt": submitted_cnt,
        "u_approved_cnt": approved_cnt,
        "u_approved_with_comment_cnt": approved_with_comment_cnt,
        "u_rejected_cnt": rejected_cnt,
        "u_avg_penalty_pct": avg_penalty_pct,
        "u_chart_labels_json": json.dumps(labels),
        "u_kills_per_month_json": json.dumps(kills_per_month),
        "u_paid_per_month_json": json.dumps(paid_per_month),
        "u_loss_per_month_json": json.dumps(loss_per_month),
        "u_status_labels_json": json.dumps(["submitted", "approved", "approved_with_comment", "rejected"]),
        "u_status_values_json": json.dumps([submitted_cnt, approved_cnt, approved_with_comment_cnt, rejected_cnt]),
        "discord_form": form,
        "my_srp_requests": my_srp_requests,
    }

    existing_context = locals().get("context", {})
    if not isinstance(existing_context, dict):
        existing_context = {}
    existing_context.update(user_stats_ctx)
    return render(request, "autosrp/review/user_landing.html", existing_context)
