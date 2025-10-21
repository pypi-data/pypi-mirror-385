from datetime import datetime, timedelta
import json
import re
import requests

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, ListView

from fittings.models import Doctrine
from eveuniverse.models import EveEntity, EveSolarSystem

from ..models import Submission
from ..models import OrgFilter
from ..tasks import process_submission

"""Form helpers and utilities"""
def _doctrine_choices():
    return [(d.id, d.name) for d in Doctrine.objects.all().order_by("name")]


class SubmissionForm(forms.ModelForm):
    doctrine_id = forms.ChoiceField(
        label="Doctrine",
        choices=(),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Select the doctrine used for this fleet (from aa-fittings).",
    )
    systems = forms.CharField(
        label="Systems",
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "placeholder": "30003307,30000142",
                "class": "form-control",
            }
        ),
        help_text="Comma-separated EVE system IDs. Example: 30003307,30000142",
        required=False,
    )
    start_at = forms.DateTimeField(
        label="Start (UTC)",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        help_text="When the SRP window begins (UTC).",
        required=False,
    )
    end_at = forms.DateTimeField(
        label="End (UTC)",
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        help_text="When the SRP window ends (UTC). If blank, defaults to +2 hours.",
    )
    battle_report_url = forms.CharField(
        label="Battle Report URL",
        required=False,
        widget=forms.URLInput(attrs={"class": "form-control", "placeholder": "zKill related or EVE Tools BR URL"}),
        help_text="Paste a zKill related link or an EVE Tools BR link to auto-fill systems and time.",
    )
    time_window_hours = forms.IntegerField(
        label="Time Window (hours)",
        required=False,
        initial=2,
        min_value=1,
        max_value=24,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        help_text="Used for zKill related links. Default is 2 hours.",
    )

    class Meta:
        model = Submission
        fields = (
            "doctrine_id",
            "systems",
            "start_at",
            "end_at",
            "strict_mode",
            "org_filter",
            "battle_report_url",
            "time_window_hours",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctrine_id"].choices = _doctrine_choices()
        if "org_filter" in self.fields:
            f = self.fields["org_filter"]
            f.widget.attrs.setdefault("class", "form-select")
            try:
                if not self.is_bound and (getattr(self.instance, "org_filter_id", None) is None):
                    default_filter = OrgFilter.objects.filter(is_default=True).order_by("id").first()
                    if default_filter:
                        f.initial = default_filter.pk
                        # Provide hint for frontend fallback (in case of empty_label or custom rendering)
                        f.widget.attrs["data-default-id"] = str(default_filter.pk)
            except Exception:
                pass
        if "strict_mode" in self.fields:
            self.fields["strict_mode"].widget.attrs.setdefault("class", "form-check-input")

    def _as_utc(self, dt):
        if dt is None:
            return None
        if timezone.is_naive(dt):
            return timezone.make_aware(dt, timezone.utc)
        return dt.astimezone(timezone.utc)

    def clean_systems(self):
        raw = (self.data.get("systems") or "").strip()
        if not raw:
            return []
        try:
            systems = [int(s.strip()) for s in raw.split(",") if s.strip()]
        except ValueError:
            raise forms.ValidationError("Systems must be a comma-separated list of numeric system IDs.")
        if not systems:
            raise forms.ValidationError("Please provide at least one system ID or a Battle Report URL.")
        return systems

    def _parse_zkill_related(self, url: str, hours_default: int) -> tuple[list[int], datetime, datetime]:
        m = re.match(r"https?://(?:beta\.)?zkillboard\.com/related/(?P<sid>\d{6,9})/(?P<stamp>\d{12})/?", url)
        if not m:
            raise ValueError("Not a zKill 'related' URL")
        system_id = int(m.group("sid"))
        stamp = m.group("stamp")
        start_at = datetime.strptime(stamp, "%Y%m%d%H%M")
        start_at = timezone.make_aware(start_at, timezone.utc)
        try:
            hours = int(self.cleaned_data.get("time_window_hours") or hours_default)
        except Exception:
            hours = hours_default
        end_at = start_at + timedelta(hours=max(1, min(hours, 24)))
        return [system_id], start_at, end_at

    def _parse_evetools_br(self, url: str) -> tuple[list[int], datetime | None, datetime | None]:
        m = re.match(r"https?://br\.evetools\.org/br/(?P<brid>[a-z0-9]+)", url.strip().lower())
        if not m:
            raise ValueError("Not an EVE Tools BR URL")
        brid = m.group("brid")
        systems: set[int] = set()
        t_min: datetime | None = None
        t_max: datetime | None = None

        sess = requests.Session()
        sess.headers.update({"User-Agent": "aa-autosrp"})
        timeout = 45

        def _maybe_add_system(obj):
            if not isinstance(obj, dict):
                return
            for key in ("system_id", "solar_system_id", "solarSystemID", "solarSystemId"):
                if key in obj:
                    try:
                        systems.add(int(obj[key]))
                    except Exception:
                        pass
            sys_obj = obj.get("system") or obj.get("solar_system") or obj.get("solarSystem") or {}
            if isinstance(sys_obj, dict):
                for k in ("id", "system_id", "solar_system_id"):
                    if k in sys_obj:
                        try:
                            systems.add(int(sys_obj[k]))
                        except Exception:
                            pass
            for arr_key in ("systems", "solar_systems", "solarSystems"):
                arr = obj.get(arr_key)
                if isinstance(arr, (list, tuple)):
                    for it in arr:
                        if isinstance(it, dict):
                            for k in ("id", "system_id", "solar_system_id"):
                                if k in it:
                                    try:
                                        systems.add(int(it[k]))
                                    except Exception:
                                        pass

        def _maybe_add_time(obj):
            nonlocal t_min, t_max
            if not isinstance(obj, dict):
                return
            for key in ("killmail_time", "kill_time", "occurred_at", "timestamp", "time", "date"):
                if key not in obj:
                    continue
                val = obj[key]
                dt_val = None
                try:
                    iv = int(val)
                    if iv > 10_000_000_000:
                        iv //= 1000
                    dt_val = datetime.utcfromtimestamp(iv).replace(tzinfo=timezone.utc)
                except Exception:
                    try:
                        from django.utils.dateparse import parse_datetime
                        dt_parsed = parse_datetime(str(val))
                        if dt_parsed is not None:
                            dt_val = dt_parsed.astimezone(timezone.utc) if timezone.is_aware(dt_parsed) else timezone.make_aware(dt_parsed, timezone.utc)
                    except Exception:
                        dt_val = None
                if dt_val is not None:
                    t_min = dt_val if (t_min is None or dt_val < t_min) else t_min
                    t_max = dt_val if (t_max is None or dt_val > t_max) else t_max

        def _walk(obj):
            if isinstance(obj, dict):
                _maybe_add_system(obj)
                _maybe_add_time(obj)
                for v in obj.values():
                    _walk(v)
            elif isinstance(obj, (list, tuple, set)):
                for v in obj:
                    _walk(v)

        r2 = sess.get(f"https://br.evetools.org/br/{brid}", timeout=timeout)
        if r2.ok:
            html = r2.text or ""
            candidates = re.findall(
                r"<script[^>]*>\s*(?:window\.__.*?=|var\s+\w+\s*=)?\s*(\{.*?\})\s*<\/script>",
                html,
                flags=re.DOTALL | re.IGNORECASE,
            )
            for blob in candidates:
                try:
                    data2 = json.loads(blob)
                except Exception:
                    continue
                _walk(data2)
                if systems and (t_min or t_max):
                    break

        return (sorted({int(s) for s in systems}), t_min, t_max)

    def clean(self):
        cleaned = super().clean()

        br_url = (cleaned.get("battle_report_url") or "").strip()
        systems = cleaned.get("systems") or []
        start = cleaned.get("start_at")
        end = cleaned.get("end_at")

        start = self._as_utc(start) if start else None
        end = self._as_utc(end) if end else None

        if br_url:
            zkill_related = re.match(r"https?://(?:beta\.)?zkillboard\.com/related/\d{6,9}/\d{12}/?", br_url)
            evetools_br = re.match(r"https?://br\.evetools\.org/br/[a-z0-9]+", br_url.strip().lower())

            if zkill_related:
                try:
                    sys_ids, auto_start, auto_end = self._parse_zkill_related(
                        br_url, int(cleaned.get("time_window_hours") or 2)
                    )
                    systems = sys_ids
                    start = auto_start
                    end = end or auto_end
                except Exception:
                    self.add_error("battle_report_url", "Could not parse zKill related URL.")
            elif evetools_br:
                try:
                    sys_ids, t_min, t_max = self._parse_evetools_br(br_url)
                    systems = sys_ids
                    if t_min and t_max:
                        start = t_min
                        end = t_max
                    elif t_min and not start:
                        start = t_min
                        end = start + timedelta(hours=2)
                except Exception:
                    self.add_error("battle_report_url", "Could not parse EVE Tools BR URL.")
            else:
                self.add_error("battle_report_url", "Unsupported Battle Report URL.")

            if not cleaned.get("org_filter"):
                self.add_error("org_filter", "Please select an Organization Filter for this submission.")

        if not br_url and not systems:
            self.add_error("systems", "Please provide systems (or a valid Battle Report URL).")
            return cleaned

        if not start:
            self.add_error("start_at", "Start time is required (or must be derived from the URL).")
            return cleaned

        if end and end <= start:
            self.add_error("end_at", "End must be after start.")
            return cleaned

        if not end:
            try:
                hours = int(cleaned.get("time_window_hours") or 2)
            except Exception:
                hours = 2
            end = start + timedelta(hours=max(1, min(hours, 24)))

        cleaned["systems"] = systems
        cleaned["start_at"] = start
        cleaned["duration_minutes"] = int((end - start).total_seconds() // 60) or 1

        try:
            cleaned["doctrine_id"] = int(cleaned.get("doctrine_id"))
        except (TypeError, ValueError):
            self.add_error("doctrine_id", "Invalid doctrine selection.")
        return cleaned


"""Submission CRUD and listing"""
class SubmissionDeleteView(PermissionRequiredMixin, View):
    permission_required = "autosrp.manage"

    def post(self, request, submission_id: int):
        sub = get_object_or_404(Submission, pk=submission_id)
        sub_id = sub.id
        sub.delete()
        messages.success(request, f"Deleted submission #{sub_id} and its kills.")
        return redirect("autosrp:review-list")


class SubmissionCreateView(PermissionRequiredMixin, FormView):
    permission_required = "autosrp.submit"
    template_name = "autosrp/fc/submit.html"
    form_class = SubmissionForm
    success_url = reverse_lazy("autosrp:my-submissions")

    def form_valid(self, form):
        sub = Submission.objects.create(
            fc=self.request.user,
            systems=form.cleaned_data["systems"],
            doctrine_id=form.cleaned_data["doctrine_id"],
            start_at=form.cleaned_data["start_at"],
            duration_minutes=form.cleaned_data["duration_minutes"],
            strict_mode=form.cleaned_data["strict_mode"],
            org_filter=form.cleaned_data["org_filter"],
        )
        process_submission.delay(sub.id)
        return super().form_valid(form)


class MySubmissionsView(PermissionRequiredMixin, ListView):
    permission_required = "autosrp.submit"
    model = Submission
    template_name = "autosrp/fc/my_submissions.html"
    paginate_by = 25

    def get_queryset(self):
        return Submission.objects.filter(fc=self.request.user).order_by("-created")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        submissions = list(ctx.get("object_list", []))

        system_ids = set()
        for s in submissions:
            try:
                for sid in (s.systems or []):
                    system_ids.add(int(sid))
            except Exception:
                continue

        names_map = {}
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

        doctrine_ids = {int(s.doctrine_id) for s in submissions if getattr(s, "doctrine_id", None)}
        doctrine_map = {}
        try:
            rows = Doctrine.objects.filter(id__in=doctrine_ids).values("id", "name")
            doctrine_map = {int(r["id"]): r["name"] for r in rows}
        except Exception:
            doctrine_map = {}

        for s in submissions:
            try:
                did = int(s.doctrine_id) if s.doctrine_id is not None else None
                s.doctrine_name = doctrine_map.get(did, f"Doctrine {did}") if did is not None else ""
            except Exception:
                s.doctrine_name = f"Doctrine {getattr(s, 'doctrine_id', '')}"

        return ctx


"""AJAX system lookup"""
class SystemLookupView(PermissionRequiredMixin, View):
    permission_required = "autosrp.submit"

    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        try:
            limit = max(1, min(int(request.GET.get("limit", 20)), 50))
        except ValueError:
            limit = 20

        data = []
        if q:
            try:
                qs = (
                    EveSolarSystem.objects.select_related("eve_constellation__eve_region")
                    .filter(name__icontains=q)
                    .order_by("name")[:limit]
                )
                for s in qs:
                    region = getattr(getattr(s.eve_constellation, "eve_region", None), "name", "")
                    data.append({"id": s.id, "name": s.name, "region": region})
            except Exception:
                data = []

        return JsonResponse(data, safe=False)
