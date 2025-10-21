from decimal import Decimal
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

try:
    from eveuniverse.models import EveType
except Exception:
    EveType = None


class ItemPrices(models.Model):
    eve_type = models.OneToOneField(
        EveType,
        on_delete=models.deletion.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)s",
        unique=True,
    )
    buy = models.DecimalField(max_digits=20, decimal_places=2)
    sell = models.DecimalField(max_digits=20, decimal_places=2)
    updated = models.DateTimeField()

    class Meta:
        verbose_name = "Item Price"
        verbose_name_plural = "Item Prices"
        ordering = ["-updated"]

    def __str__(self):
        name = getattr(getattr(self, "eve_type", None), "name", None)
        return f"{name or self.eve_type_id} — sell:{self.sell} buy:{self.buy}"


class PenaltyScheme(models.Model):
    name = models.CharField(max_length=64, unique=True)
    per_wrong_module_pct   = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("10.00"))
    per_missing_module_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    per_extra_module_pct   = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    count_rigs = models.BooleanField(default=True)
    count_subsystems = models.BooleanField(default=True)
    relax_substitutions_no_penalty = models.BooleanField(default=True)
    max_total_deduction_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("50.00"))
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Penalty Scheme"
        verbose_name_plural = "Penalty Schemes"

    def __str__(self):
        return self.name


class DoctrineReward(models.Model):
    doctrine_id = models.PositiveIntegerField(db_index=True)
    ship_type_id = models.BigIntegerField(db_index=True)
    base_reward_isk = models.DecimalField(max_digits=18, decimal_places=2)
    penalty_scheme = models.ForeignKey(PenaltyScheme, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.CharField(max_length=200, blank=True, default="")
    doctrine_fit_id = models.PositiveIntegerField(db_index=True, default=1)

    class Meta:
        verbose_name = "Base Reward"
        verbose_name_plural = "Base Rewards"
        constraints = [
            models.UniqueConstraint(fields=["doctrine_fit_id"], name="unique_reward_per_doctrine_fit"),
        ]


class AppSetting(models.Model):
    active = models.BooleanField(default=True)
    default_penalty_scheme = models.ForeignKey(PenaltyScheme, null=True, on_delete=models.SET_NULL)
    default_duration_minutes = models.PositiveIntegerField(default=120, help_text="Default duration in minutes for new battle reports.")
    ignore_capsules = models.BooleanField(default=True, help_text="If enabled, kills where the victim was in a capsule are ignored.")
    discord_mute_all = models.BooleanField(default=False, help_text="If enabled, all users will be not receive notifications in Discord.")

    class Meta:
        verbose_name = "App Setting"
        verbose_name_plural = "App Settings"


class OrgFilter(models.Model):
    name = models.CharField(max_length=100, default="Default")
    alliance_ids = models.JSONField(default=list, blank=True)
    corporation_ids = models.JSONField(default=list, blank=True)
    is_default = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Organization Filter"
        verbose_name_plural = "Organization Filters"
        ordering = ["name"]

    def __str__(self) -> str:
        return (self.name or "").strip() or f"OrgFilter #{self.pk}"


class Submission(models.Model):
    fc = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    systems = models.JSONField()  # list[int]
    doctrine_id = models.PositiveIntegerField()
    start_at = models.DateTimeField()  # UTC
    duration_minutes = models.PositiveIntegerField(default=120)
    strict_mode = models.BooleanField(default=True)
    org_filter = models.ForeignKey(OrgFilter, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, default="queued")  # queued|processing|done|error
    error = models.TextField(blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        verbose_name = "Battle Report"
        verbose_name_plural = "Battle Reports"
        ordering = ["-created"]
        permissions = [
            ("manage",  "Can manage Auto SRP settings"),
            ("submit",  "Can submit Auto SRP requests"),
            ("review",  "Can review Auto SRP batches"),
        ]


class KillRecord(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="kills")
    killmail_id = models.BigIntegerField(unique=True)
    killmail_hash = models.CharField(max_length=64)
    zkb_url = models.URLField()
    occurred_at = models.DateTimeField()
    system_id = models.BigIntegerField()
    victim_char_id = models.BigIntegerField()
    victim_corp_id = models.BigIntegerField()
    victim_alliance_id = models.BigIntegerField(null=True)
    ship_type_id = models.BigIntegerField()
    fitted_type_ids = models.JSONField(default=list)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=21,
        default="submitted",  # submitted | approved | approved_with_comment | rejected
        choices=[
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("approved_with_comment", "Approved with Comment"),
            ("rejected", "Rejected")
        ]
    )
    status_comment = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Kill Record"
        verbose_name_plural = "Kill Records"


class FitCheck(models.Model):
    kill = models.OneToOneField(
        KillRecord,
        on_delete=models.CASCADE,
        related_name="fitcheck",
    )
    doctrine_fit_id = models.PositiveIntegerField()
    mode = models.CharField(max_length=12, default="strict")  # strict|relaxed
    passed = models.BooleanField(default=False)
    missing = models.JSONField(default=dict)
    extra = models.JSONField(default=dict)
    substitutions = models.JSONField(default=list)
    notes = models.TextField(blank=True, default="")


    class Meta:
        verbose_name = "Fit Check"
        verbose_name_plural = "Fit Checks"


class PayoutSuggestion(models.Model):
    kill = models.OneToOneField(KillRecord, on_delete=models.CASCADE, related_name="payout")
    base_reward_isk = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    penalty_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    penalty_breakdown = models.JSONField(default=dict)
    suggested_isk = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    hull_price_isk = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    fit_price_isk = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    override_isk = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Payout Suggestion"
        verbose_name_plural = "Payout Suggestions"

    @property
    def final_isk(self):
        return self.override_isk if self.override_isk is not None else self.suggested_isk

class PayoutRecord(models.Model):
    kill = models.OneToOneField("KillRecord", on_delete=models.CASCADE, related_name="payout_record")
    suggested_isk = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    actual_isk = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    system_id = models.BigIntegerField(default=0)
    system_name = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        verbose_name = "Payout Record"
        verbose_name_plural = "Payout Records"

    def __str__(self) -> str:
        return f"PayoutRecord(kill={self.kill_id}, actual={self.actual_isk})"

class DiscordNotificationSetting(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="discord_setting")
    discord_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Setting"
        verbose_name_plural = "User Settings"

    def __str__(self) -> str:
        return f"DiscordNotificationSetting(user={self.user_id}, enabled={self.discord_enabled})"

class IgnoredModule(models.Model):
    eve_type_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255, db_index=True)
    added_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Ignored Module"
        verbose_name_plural = "Ignored Modules"

    def __str__(self) -> str:
        return f"{self.name} ({self.eve_type_id})"

@receiver(post_save, sender=get_user_model())
def create_discord_setting_for_user(sender, instance, created, **kwargs):
    if created:
        DiscordNotificationSetting.objects.get_or_create(user=instance)
