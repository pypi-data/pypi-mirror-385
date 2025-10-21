"""App Configuration"""

# Django
from django.apps import AppConfig

from autosrp import __version__

class AutoSRPConfig(AppConfig):

    name = "autosrp"
    label = "autosrp"
    verbose_name = f"Auto SRP v{__version__}"
