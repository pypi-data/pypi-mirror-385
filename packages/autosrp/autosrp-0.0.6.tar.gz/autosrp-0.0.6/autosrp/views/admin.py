from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count, F, DecimalField, Q, ExpressionWrapper, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.views import View
from django.contrib import messages
from django import forms

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
import json

from eveuniverse.models import EveType
from ..models import IgnoredModule

from ..forms import PenaltyForm
from ..models import (
    Submission,
    KillRecord,
    PayoutSuggestion,
    PayoutRecord,
    PenaltyScheme,
    DoctrineReward,
    AppSetting,
)

"""Helpers: doctrine and hull choices"""
def _doctrine_choices():
    try:
        from fittings.models import Doctrine
        choices = list(Doctrine.objects.values_list("id", "name"))
        if choices:
            return choices
    except Exception:
        pass
    try:
        from fittings.models import Fitting
        ids = (
            Fitting.objects.exclude(doctrine_id__isnull=True)
            .values_list("doctrine_id", flat=True)
            .distinct()
            .order_by("doctrine_id")
        )
        return [(int(i), f"Doctrine {i}") for i in ids]
    except Exception:
        return []


def _hull_choices_for_doctrine(doctrine_id: int) -> list[tuple[int, str]]:
    if not doctrine_id:
        return []
    ship_ids: list[int] = []
    try:
        from fittings.models import Fitting
        ship_ids = list(
            Fitting.objects.filter(doctrines__id=int(doctrine_id))
            .values_list("ship_type_id", flat=True)
            .distinct()
        )
    except Exception:
        ship_ids = []
    if not ship_ids:
        return []

    names: dict[int, str] = {}
    try:
        from eveuniverse.models import EveType
        rows = EveType.objects.filter(id__in=ship_ids).values("id", "name")
        names = {int(r["id"]): (r["name"] or f"Type {r['id']}") for r in rows}
    except Exception:
        names = {}

    out = []
    for sid in sorted({int(x) for x in ship_ids}):
        label = names.get(int(sid), f"Type {sid}")
        out.append((int(sid), label))
    return out


"""AJAX endpoints"""
@require_GET
def doctrine_hulls(request):
    try:
        did = int(request.GET.get("doctrine_id", 0) or 0)
    except (TypeError, ValueError):
        did = 0

    hulls: list[dict] = []
    if did > 0:
        try:
            from fittings.models import Fitting
            ship_ids = list(
                Fitting.objects.filter(doctrines__id=did)
                .values_list("ship_type_id", flat=True)
                .distinct()
            )
            if ship_ids:
                try:
                    from eveuniverse.models import EveType
                    rows = EveType.objects.filter(id__in=ship_ids).values("id", "name")
                    hulls = [{"id": int(r["id"]), "name": (r["name"] or f"Type {r['id']}")} for r in rows]
                except Exception:
                    hulls = [{"id": int(sid), "name": f"Type {int(sid)}"} for sid in ship_ids]
        except Exception:
            hulls = []

    try:
        hulls.sort(key=lambda x: (x["name"] or str(x["id"])).lower())
    except Exception:
        pass

    return JsonResponse({"hulls": hulls})


@require_GET
def doctrine_fits(request):
    try:
        did = int(request.GET.get("doctrine_id", 0) or 0)
        sid = int(request.GET.get("ship_type_id", 0) or 0)
    except (TypeError, ValueError):
        return JsonResponse({"fits": []})

    fits: list[dict] = []
    if did > 0 and sid > 0:
        try:
            from fittings.models import Fitting
            qs = (
                Fitting.objects.filter(doctrines__id=did, ship_type_id=sid)
                .values("id", "name")
                .order_by("name", "id")
            )
            fits = [{"id": int(r["id"]), "name": (r["name"] or f"Fit {r['id']}")} for r in qs]
        except Exception:
            fits = []

    return JsonResponse({"fits": fits})


"""Forms"""
class RewardForm(forms.ModelForm):
    doctrine_id = forms.ChoiceField(
        choices=[("", "— Select a doctrine —")] + _doctrine_choices(),
        label="Doctrine",
        required=True,
    )
    ship_type_id = forms.ChoiceField(
        choices=[("", "— Select a doctrine first —")],
        label="Ship (from doctrine fits)",
        required=True,
    )
    doctrine_fit_id = forms.ChoiceField(
        choices=[("", "— Select a ship first —")],
        label="Fit",
        required=True,
    )

    class Meta:
        model = DoctrineReward
        fields = ("doctrine_id", "ship_type_id", "doctrine_fit_id", "base_reward_isk", "penalty_scheme", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        selected_doctrine = None
        data = self.data or None
        if data and str(data.get("doctrine_id", "")).strip():
            try:
                selected_doctrine = int(data.get("doctrine_id"))
            except (TypeError, ValueError):
                selected_doctrine = None
        elif getattr(self.instance, "doctrine_id", None):
            selected_doctrine = int(self.instance.doctrine_id)

        if selected_doctrine:
            hull_choices = _hull_choices_for_doctrine(selected_doctrine) or []
            if hull_choices:
                self.fields["ship_type_id"].choices = [("", "— Select a ship —")] + [(str(a), b) for a, b in hull_choices]
            else:
                self.fields["ship_type_id"].choices = [("", "— No fits for this doctrine —")]
        else:
            self.fields["ship_type_id"].choices = [("", "— Select a doctrine first —")]

        selected_ship = None
        if data and str(data.get("ship_type_id", "")).strip():
            try:
                selected_ship = int(data.get("ship_type_id"))
            except (TypeError, ValueError):
                selected_ship = None
        elif getattr(self.instance, "ship_type_id", None) and selected_doctrine:
            selected_ship = int(self.instance.ship_type_id)

        if selected_doctrine and selected_ship:
            try:
                from fittings.models import Fitting
                rows = (
                    Fitting.objects.filter(doctrines__id=selected_doctrine, ship_type_id=selected_ship)
                    .values("id", "name")
                    .order_by("name", "id")
                )
                fit_choices = [(str(int(r["id"])), (r["name"] or f"Fit {r['id']}")) for r in rows]
                if fit_choices:
                    self.fields["doctrine_fit_id"].choices = [("", "— Select a fit —")] + fit_choices
                else:
                    self.fields["doctrine_fit_id"].choices = [("", "— No fits for this ship —")]
            except Exception:
                self.fields["doctrine_fit_id"].choices = [("", "— No fits for this ship —")]
        else:
            self.fields["doctrine_fit_id"].choices = [("", "— Select a ship first —")]

        self.fields["doctrine_id"].coerce = int if hasattr(self.fields["doctrine_id"], "coerce") else None
        self.fields["ship_type_id"].coerce = int if hasattr(self.fields["ship_type_id"], "coerce") else None
        self.fields["doctrine_fit_id"].coerce = int if hasattr(self.fields["doctrine_fit_id"], "coerce") else None

        self.fields["base_reward_isk"].label = "Base Reward (ISK)"

    def clean(self):
        cleaned = super().clean()

        try:
            did = int(cleaned.get("doctrine_id"))
        except Exception:
            did = None
        try:
            sid = int(cleaned.get("ship_type_id"))
        except Exception:
            sid = None
        try:
            fid = int(cleaned.get("doctrine_fit_id"))
        except Exception:
            fid = None

        if not did:
            raise ValidationError({"doctrine_id": "Please select a doctrine."})
        if not sid:
            raise ValidationError({"ship_type_id": "Please select a ship."})
        if not fid:
            raise ValidationError({"doctrine_fit_id": "Please select a fit for the selected ship."})

        valid_hulls = {hid for hid, _ in _hull_choices_for_doctrine(did)}
        if sid not in valid_hulls:
            raise ValidationError({"ship_type_id": "Selected ship is not available in the chosen doctrine."})

        try:
            from fittings.models import Fitting
            exists = Fitting.objects.filter(doctrines__id=did, ship_type_id=sid, id=fid).exists()
        except Exception:
            exists = False
        if not exists:
            raise ValidationError({"doctrine_fit_id": "Selected fit is not part of the chosen doctrine and ship."})

        cleaned["doctrine_id"] = did
        cleaned["ship_type_id"] = sid
        cleaned["doctrine_fit_id"] = fid
        return cleaned


"""Views: settings and lists"""
class SettingsHome(PermissionRequiredMixin, TemplateView):
    permission_required = "autosrp.manage"
    template_name = "autosrp/admin/home.html"

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        app = AppSetting.objects.first()
        if app is None:
            try:
                app = AppSetting.objects.create(active=True)
            except Exception:
                app = None
        ctx["app"] = app

        try:
            ctx["penalty_schemes"] = list(PenaltyScheme.objects.all().values("id", "name"))
        except Exception:
            ctx["penalty_schemes"] = []

        try:
            from autosrp.models import IgnoredModule
            ctx["ignored_count"] = int(IgnoredModule.objects.count())
        except Exception:
            ctx["ignored_count"] = 0
        return ctx

    def post(self, request, **kw):
        if not request.user.has_perm("autosrp.manage"):
            return HttpResponseForbidden("You do not have permission to perform this action.")
        app = AppSetting.objects.first()
        if app is None:
            app = AppSetting.objects.create(active=True)

        active = bool(request.POST.get("active"))
        ignore_capsules = bool(request.POST.get("ignore_capsules"))
        discord_mute_all = bool(request.POST.get("discord_mute_all"))

        try:
            duration = int(request.POST.get("default_duration_minutes") or 0)
            if duration <= 0:
                duration = app.default_duration_minutes or 120
        except Exception:
            duration = app.default_duration_minutes or 120

        dps_raw = (request.POST.get("default_penalty_scheme") or "").strip()
        dps_obj = None
        if dps_raw:
            try:
                dps_id = int(dps_raw)
                dps_obj = PenaltyScheme.objects.filter(pk=dps_id).first()
            except Exception:
                dps_obj = None

        app.active = active
        app.default_duration_minutes = duration
        app.ignore_capsules = ignore_capsules
        app.discord_mute_all = discord_mute_all
        app.default_penalty_scheme = dps_obj
        app.save()

        messages.success(request, "Updated application settings.")
        return redirect("autosrp:admin-home")


class PenaltyList(PermissionRequiredMixin, ListView):
    permission_required = "autosrp.manage"
    model = PenaltyScheme
    template_name = "autosrp/admin/penalty_list.html"


class PenaltyDelete(PermissionRequiredMixin, View):
    permission_required = "autosrp.manage"

    def post(self, request, pk: int):
        obj = get_object_or_404(PenaltyScheme, pk=pk)
        name = str(obj.name or f"Scheme {obj.pk}")
        obj.delete()
        messages.success(request, f"Deleted penalty scheme '{name}'.")
        return redirect("autosrp:penalty-list")


class PenaltyCreate(PermissionRequiredMixin, CreateView):
    permission_required = "autosrp.manage"
    model = PenaltyScheme
    form_class = PenaltyForm
    success_url = reverse_lazy("autosrp:penalty-list")
    template_name = "autosrp/admin/penalty_form.html"


class PenaltyUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "autosrp.manage"
    model = PenaltyScheme
    form_class = PenaltyForm
    success_url = reverse_lazy("autosrp:penalty-list")
    template_name = "autosrp/admin/penalty_form.html"


class RewardList(PermissionRequiredMixin, ListView):
    permission_required = "autosrp.manage"
    model = DoctrineReward
    template_name = "autosrp/admin/reward_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        rewards = list(ctx.get("object_list", []))

        fit_ids = {int(r.doctrine_fit_id) for r in rewards if getattr(r, "doctrine_fit_id", None)}
        ship_ids = {int(r.ship_type_id) for r in rewards if getattr(r, "ship_type_id", None)}

        fit_map = {}
        try:
            from fittings.models import Fitting
            rows = Fitting.objects.filter(id__in=fit_ids).values("id", "name")
            fit_map = {int(r["id"]): (r["name"] or f"Fit {r['id']}") for r in rows}
        except Exception:
            fit_map = {}

        type_map = {}
        try:
            from eveuniverse.models import EveType
            rows = EveType.objects.filter(id__in=ship_ids).values("id", "name")
            type_map = {int(r["id"]): (r["name"] or f"Type {r['id']}") for r in rows}
        except Exception:
            type_map = {}

        for r in rewards:
            try:
                r.fit_name = fit_map.get(int(r.doctrine_fit_id), f"Fit {int(r.doctrine_fit_id)}")
            except Exception:
                r.fit_name = f"Fit {getattr(r, 'doctrine_fit_id', '')}"
            try:
                r.ship_name = type_map.get(int(r.ship_type_id), f"Type {int(r.ship_type_id)}")
            except Exception:
                r.ship_name = f"Type {getattr(r, 'ship_type_id', '')}"

        ctx["object_list"] = rewards
        return ctx


class RewardCreate(PermissionRequiredMixin, CreateView):
    permission_required = "autosrp.manage"
    model = DoctrineReward
    form_class = RewardForm
    success_url = reverse_lazy("autosrp:reward-list")
    template_name = "autosrp/admin/reward_form.html"


class RewardUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "autosrp.manage"
    model = DoctrineReward
    form_class = RewardForm
    success_url = reverse_lazy("autosrp:reward-list")
    template_name = "autosrp/admin/reward_form.html"


class RewardDelete(PermissionRequiredMixin, View):
    permission_required = "autosrp.manage"

    def post(self, request, pk: int):
        obj = get_object_or_404(DoctrineReward, pk=pk)
        did, sid = int(obj.doctrine_id), int(obj.ship_type_id)
        obj.delete()
        messages.success(request, f"Deleted reward for Doctrine {did} / Ship {sid}.")
        return redirect("autosrp:reward-list")


"""Statistics"""
@login_required
def stats(request):
    user = request.user
    if not (user.has_perm("autosrp.review") or user.has_perm("autosrp.manage") or user.is_superuser):
        return HttpResponseForbidden("You do not have permission to view this page.")

    """Totals"""
    total_fights = Submission.objects.count()
    total_kills = KillRecord.objects.count()

    """Aggregations"""
    loss_value_expr = ExpressionWrapper(
        F("hull_price_isk") + F("fit_price_isk"),
        output_field=DecimalField(max_digits=20, decimal_places=2),
    )
    total_loss = (
        PayoutSuggestion.objects.annotate(loss_value=loss_value_expr)
        .aggregate(
            total=Coalesce(
                Sum("loss_value"),
                Value(Decimal("0.00"), output_field=DecimalField(max_digits=20, decimal_places=2)),
            )
        )
        .get("total")
    )
    total_paid = (
        PayoutRecord.objects.aggregate(
            total=Coalesce(
                Sum("actual_isk"),
                Value(Decimal("0.00"), output_field=DecimalField(max_digits=20, decimal_places=2)),
            )
        ).get("total")
    )
    avg_kills_per_fight = (total_kills / total_fights) if total_fights else 0
    avg_loss_per_fight = (total_loss / total_fights) if total_fights else 0
    avg_paid_per_fight = (total_paid / total_fights) if total_fights else 0
    avg_suggested_per_kill = (
        PayoutSuggestion.objects.aggregate(
            v=Coalesce(
                Avg("suggested_isk"),
                Value(Decimal("0.00"), output_field=DecimalField(max_digits=20, decimal_places=2)),
            )
        ).get("v")
    )
    avg_final_per_kill = (
        PayoutSuggestion.objects.annotate(
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
    approved_cnt = KillRecord.objects.filter(Q(status="approved") | Q(status="approved_with_comment")).count()
    rejected_cnt = KillRecord.objects.filter(status="rejected").count()
    submitted_cnt = KillRecord.objects.filter(status="submitted").count()
    avg_penalty_pct = (
        PayoutSuggestion.objects.aggregate(
            v=Coalesce(
                Avg("penalty_pct"),
                Value(Decimal("0.00"), output_field=DecimalField(max_digits=5, decimal_places=2)),
            )
        ).get("v")
    )

    """Charts"""
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
        KillRecord.objects.filter(occurred_at__gte=start_month)
        .annotate(m=TruncMonth("occurred_at"))
        .values("m")
        .annotate(c=Count("id"))
        .order_by("m")
    )
    kills_map = {ym(r["m"]): r["c"] for r in kills_qs}
    kills_per_month = [kills_map.get(label, 0) for label in labels]

    paid_qs = (
        PayoutRecord.objects.filter(kill__occurred_at__gte=start_month)
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
        PayoutSuggestion.objects.filter(kill__occurred_at__gte=start_month)
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

    """Status distribution"""
    status_labels = ["submitted", "approved", "approved_with_comment", "rejected"]
    status_values = [
        KillRecord.objects.filter(status="submitted").count(),
        KillRecord.objects.filter(status="approved").count(),
        KillRecord.objects.filter(status="approved_with_comment").count(),
        KillRecord.objects.filter(status="rejected").count(),
    ]

    context = {
        "total_loss": total_loss,
        "total_paid": total_paid,
        "total_fights": total_fights,
        "total_kills": total_kills,
        "avg_kills_per_fight": avg_kills_per_fight,
        "avg_loss_per_fight": avg_loss_per_fight,
        "avg_paid_per_fight": avg_paid_per_fight,
        "avg_suggested_per_kill": avg_suggested_per_kill,
        "avg_final_per_kill": avg_final_per_kill,
        "approved_cnt": approved_cnt,
        "rejected_cnt": rejected_cnt,
        "submitted_cnt": submitted_cnt,
        "avg_penalty_pct": avg_penalty_pct,
        "chart_labels_json": json.dumps(labels),
        "kills_per_month_json": json.dumps(kills_per_month),
        "paid_per_month_json": json.dumps(paid_per_month),
        "loss_per_month_json": json.dumps(loss_per_month),
        "status_labels_json": json.dumps(status_labels),
        "status_values_json": json.dumps(status_values),
    }
    return render(request, "autosrp/admin/stats.html", context)


class IgnoredModuleList(PermissionRequiredMixin, TemplateView):
    permission_required = "autosrp.manage"
    template_name = "autosrp/admin/ignored_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["items"] = list(IgnoredModule.objects.order_by("name").values("id", "name", "eve_type_id"))
        return ctx

    def post(self, request, **kwargs):
        action = (request.POST.get("action") or "").strip()
        if action == "add":
            raw = (request.POST.get("eve_type_id") or "").strip()
            try:
                tid = int(raw)
            except Exception:
                return redirect("autosrp:ignored-modules")
            row = EveType.objects.filter(id=tid).values("id", "name").first()
            if not row:
                return redirect("autosrp:ignored-modules")
            IgnoredModule.objects.get_or_create(
                eve_type_id=int(row["id"]),
                defaults={"name": row["name"] or f"Type {row['id']}", "added_by": request.user},
            )
            return redirect("autosrp:ignored-modules")
        elif action == "delete":
            try:
                pk = int(request.POST.get("id") or 0)
                IgnoredModule.objects.filter(id=pk).delete()
            except Exception:
                pass
            return redirect("autosrp:ignored-modules")
        return redirect("autosrp:ignored-modules")


@require_GET
def api_search_modules(request):
    q = (request.GET.get("q") or "").strip()
    if not q or len(q) < 2:
        return JsonResponse({"items": []})
    rows = (
        EveType.objects.filter(name__icontains=q)
        .values("id", "name")[:25]
    )
    items = [{"id": int(r["id"]), "name": r["name"]} for r in rows]
    return JsonResponse({"items": items})
