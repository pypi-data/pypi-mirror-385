"""
Handling Discord direct messages to a user
"""

# Standard Library
from datetime import datetime
from enum import Enum
# Django
from django.contrib.auth.models import User
from django.utils import timezone

# Alliance Auth
from allianceauth.notifications import notify

# AA SRP
from autosrp import __title__
from autosrp.app_settings import (
    DISCORDPROXY_HOST,
    DISCORDPROXY_PORT,
    DISCORDPROXY_TIMEOUT,
    aa_discordnotify_installed,
    allianceauth_discordbot_installed,
    discordproxy_installed,
)
class DiscordEmbedColor(Enum):
    """
    Discord embed colors
    """

    INFO = 0x5BC0DE
    SUCCESS = 0x5CB85C
    WARNING = 0xF0AD4E
    DANGER = 0xD9534F


DISCORD_EMBED_COLOR_MAP = {
    "info": DiscordEmbedColor.INFO.value,
    "success": DiscordEmbedColor.SUCCESS.value,
    "warning": DiscordEmbedColor.WARNING.value,
    "danger": DiscordEmbedColor.DANGER.value,
}



def _aadiscordbot_send_private_message(
    user_id: int,
    title: str,
    message: str,
    embed_message: bool = True,
    level: str = "info",
) -> None:
    """
    Try to send a PM to a user on Discord via allianceauth-discordbot

    :param user_id:
    :type user_id:
    :param title:
    :type title:
    :param message:
    :type message:
    :param embed_message:
    :type embed_message:
    :param level:
    :type level:
    :return:
    :rtype:
    """

    if allianceauth_discordbot_installed():

        # Third Party
        from aadiscordbot.tasks import send_message
        from discord import Embed

        embed = Embed(
            title=str(title),
            description=message,
            color=DISCORD_EMBED_COLOR_MAP.get(level),
            timestamp=datetime.now(),
        )

        if embed_message is True:
            send_message(user_id=user_id, embed=embed)
        else:
            send_message(user_id=user_id, message=f"**{title}**\n\n{message}")


def _discordproxy_send_private_message(
    user_id: int,
    title: str,
    message: str,
    embed_message: bool = True,
    level: str = "info",
):
    """
    Try to send a PM to a user on Discord via discordproxy
    (fall back to allianceauth-discordbot if needed)

    :param user_id:
    :type user_id:
    :param title:
    :type title:
    :param message:
    :type message:
    :param embed_message:
    :type embed_message:
    :param level:
    :type level:
    :return:
    :rtype:
    """

    # Third Party
    from discordproxy.client import DiscordClient
    from discordproxy.exceptions import DiscordProxyException

    target = f"{DISCORDPROXY_HOST}:{DISCORDPROXY_PORT}"
    client = DiscordClient(target=target, timeout=DISCORDPROXY_TIMEOUT)

    try:
        if embed_message is True:
            # Third Party
            from discordproxy.discord_api_pb2 import Embed

            footer = Embed.Footer(text=str(__title__))
            embed = Embed(
                title=str(title),
                description=message,
                color=DISCORD_EMBED_COLOR_MAP.get(level),
                timestamp=timezone.now().isoformat(),
                footer=footer,
            )

            client.create_direct_message(user_id=user_id, embed=embed)
        else:
            client.create_direct_message(
                user_id=user_id, content=f"**{title}**\n\n{message}"
            )
    except DiscordProxyException as ex:

        _aadiscordbot_send_private_message(
            user_id=user_id,
            level=level,
            title=title,
            message=message,
            embed_message=embed_message,
        )


def _resolve_discord_uid(user: User) -> int:
    try:
        from allianceauth.services.modules.discord.models import DiscordUser  # type: ignore
        uid = DiscordUser.objects.filter(user=user).values_list("uid", flat=True).first()
        if uid:
            return int(uid)
    except Exception:
        pass

    return 0

def send_user_notification(
    user: User,
    title: str,
    message: dict[str, str],
    embed_message: bool = True,
    level: str = "info",
) -> None:
    if message.get("allianceauth"):
        getattr(notify, level, notify.info)(user=user, title=title, message=message["allianceauth"])

    try:
        from autosrp.models import AppSetting
        app = AppSetting.objects.first()
        if app and getattr(app, "discord_mute_all", False):
            return
    except Exception:
        pass

    discord_pref_enabled = True
    try:
        setting = getattr(user, "discord_setting", None)
        if setting is not None:
            discord_pref_enabled = bool(getattr(setting, "discord_enabled", True))
    except Exception:
        discord_pref_enabled = True

    if not discord_pref_enabled:
        return

    uid = _resolve_discord_uid(user)
    if uid <= 0 or not message.get("discord"):
        return
    try:
        if discordproxy_installed():
            _discordproxy_send_private_message(
                user_id=uid,
                level=level,
                title=title,
                message=message["discord"],
                embed_message=embed_message,
            )
            return
    except Exception:
        pass

    try:
        if allianceauth_discordbot_installed():
            _aadiscordbot_send_private_message(
                user_id=uid,
                level=level,
                title=title,
                message=message["discord"],
                embed_message=embed_message,
            )
    except Exception:
        pass
