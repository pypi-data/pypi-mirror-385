from django import forms
from .models import AppSetting, PenaltyScheme, DiscordNotificationSetting

"""App Settings"""
class AppSettingForm(forms.ModelForm):
    class Meta:
        model = AppSetting
        fields = "__all__"


""" User Settings """
class DiscordSettingsForm(forms.ModelForm):
    class Meta:
        model = DiscordNotificationSetting
        fields = ["discord_enabled"]
        labels = {"discord_enabled": "Enable Discord notifications"}
        widgets = {
            "discord_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"})
        }


""" Penalty Settings """
class PenaltyForm(forms.ModelForm):
    class Meta:
        model = PenaltyScheme
        fields = "__all__"
        labels = {
            "name": "Scheme Name",
            "per_missing_module_pct": "Per Missing Module (%)",
            "per_extra_module_pct": "Per Wrong Module (%)",
            "count_rigs": "Include Rigs in Penalties",
            "count_subsystems": "Include T3 Subsystems in Penalties",
            "relax_substitutions_no_penalty": "No Penalty for Allowed Substitutions",
            "max_total_deduction_pct": "Max Total Deduction (%)",
            "is_default": "Is Default?",
        }
