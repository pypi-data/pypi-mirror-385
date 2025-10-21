"""App Settings"""

from django.conf import settings
from django.apps import apps

DISCORDPROXY_PORT = getattr(settings, "DISCORDPROXY_PORT", 50051)
DISCORDPROXY_HOST = getattr(settings, "DISCORDPROXY_HOST", "localhost")
DISCORDPROXY_TIMEOUT = getattr(settings, "DISCORDPROXY_TIMEOUT", 300)
AUTOSRP_PRICE_JANICE_API_KEY = getattr(settings, "AUTOSRP_PRICE_JANICE_API_KEY", "")
IGNORE_CATEGORY_IDS: set[int] = set(getattr(settings, "AUTOSRP_FITCHECK_IGNORE_CATEGORY_IDS", {8, 18, 20, 5}))

def allianceauth_discordbot_installed() -> bool:
    return apps.is_installed(app_name="aadiscordbot")

def aa_discordnotify_installed() -> bool:
    return apps.is_installed(app_name="discordnotify")

def discordproxy_installed() -> bool:
    try:
        from discordproxy.client import DiscordClient
    except ModuleNotFoundError:
        return False

    return True
