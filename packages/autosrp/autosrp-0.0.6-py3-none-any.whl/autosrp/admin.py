"""Admin File"""

from django.contrib import admin
from .models import (
    AppSetting,
    PenaltyScheme,
    DoctrineReward,
    OrgFilter,
    Submission,
    KillRecord,
    FitCheck,
    PayoutSuggestion,
    ItemPrices,
    PayoutRecord,
    DiscordNotificationSetting,
)

@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ("active", "default_penalty_scheme", "default_duration_minutes", "ignore_capsules")

@admin.register(PenaltyScheme)
class PenaltySchemeAdmin(admin.ModelAdmin):
    list_display = ("name", "per_wrong_module_pct", "max_total_deduction_pct", "is_default")
    list_editable = ("per_wrong_module_pct", "max_total_deduction_pct", "is_default")

@admin.register(DoctrineReward)
class DoctrineRewardAdmin(admin.ModelAdmin):
    list_display = ("doctrine_id", "ship_type_id", "base_reward_isk", "penalty_scheme")
    search_fields = ("doctrine_id", "ship_type_id")

@admin.register(OrgFilter)
class OrgFilterAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default")

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "fc", "doctrine_id", "start_at", "duration_minutes", "status", "created", "processed_at")
    list_filter = ("status",)

@admin.register(KillRecord)
class KillRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "submission", "killmail_id", "system_id", "occurred_at", "ship_type_id")
    search_fields = ("killmail_id",)

@admin.register(FitCheck)
class FitCheckAdmin(admin.ModelAdmin):
    list_display = ("kill", "doctrine_fit_id", "mode", "passed")

@admin.register(PayoutSuggestion)
class PayoutSuggestionAdmin(admin.ModelAdmin):
    list_display = ("kill", "base_reward_isk", "penalty_pct", "suggested_isk", "override_isk", "hull_price_isk", "fit_price_isk")

@admin.register(ItemPrices)
class ItemPricesAdmin(admin.ModelAdmin):
    list_display = ("eve_type", "sell", "buy", "updated")
    search_fields = ("eve_type__name",)

@admin.register(PayoutRecord)
class PayoutRecordAdmin(admin.ModelAdmin):
    list_display = ("kill", "suggested_isk", "actual_isk", "system_id", "system_name")
    search_fields = ("kill__killmail_id", "system_name")

@admin.register(DiscordNotificationSetting)
class DiscordNotificationSettingAdmin(admin.ModelAdmin):
    list_display = ("user", "discord_enabled", "created_at", "updated_at")
    list_filter = ("discord_enabled",)
