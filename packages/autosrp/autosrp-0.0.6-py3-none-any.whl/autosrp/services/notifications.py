"""
Notifications helper
"""

from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
import logging
from autosrp.services.discord import send_user_notification
from autosrp.models import KillRecord

log = logging.getLogger(__name__)

def notify_requester(
    requester: User,
    srp_request: KillRecord,
    message_level: str = "success",
) -> None:

    request_status = srp_request.status

    ship_display = str(getattr(srp_request, "ship_type_id", ""))
    try:
        from eveuniverse.models import EveType  # type: ignore
        row = EveType.objects.filter(id=int(srp_request.ship_type_id)).values("name").first()
        name = (row or {}).get("name")
        if name:
            ship_display = name
    except Exception:
        pass

    reviewer_display = ""
    try:
        reviewer_user = getattr(srp_request, "reviewer", None)
        if reviewer_user:
            profile = getattr(reviewer_user, "profile", None)
            main_char = getattr(profile, "main_character", None)
            if main_char and getattr(main_char, "character_name", None):
                reviewer_display = main_char.character_name
            elif main_char and getattr(main_char, "name", None):
                reviewer_display = main_char.name
            else:
                reviewer_display = getattr(reviewer_user, "username", "") or str(reviewer_user)
    except Exception:
        reviewer_display = getattr(getattr(srp_request, "reviewer", None), "username", "") or ""

    context = {
        "ship": ship_display,
        "time": srp_request.occurred_at,
        "status": (request_status or "").lower(),
        "reviewer": reviewer_display,
        "reviewed_at": getattr(srp_request, "reviewed_at", None),
        "comment": srp_request.status_comment,
        "zkb_url": getattr(srp_request, "zkb_url", ""),
    }

    try:
        allianceauth_notification = render_to_string(
            template_name="autosrp/notifications/alliance_auth_notify.html",
            context=context,
        )
    except TemplateDoesNotExist:
        allianceauth_notification = (
            f"Your SRP request for ship {context['ship']} was {context['status']}."
            + (f"\nComment: {context['comment']}" if context.get("comment") else "")
        )
        log.warning("autosrp: alliance_auth_notify template not found; using fallback text")

    try:
        discord_notification = render_to_string(
            template_name="autosrp/notifications/discord_notify.html",
            context=context,
        )
    except TemplateDoesNotExist:
        discord_notification = allianceauth_notification
        log.warning("autosrp: discord_notify template not found; using AA text fallback")

    send_user_notification(
        user=requester,
        level=message_level,
        title=f"SRP Request {request_status}",
        message={
            "allianceauth": allianceauth_notification or "SRP status updated.",
            "discord": discord_notification or "SRP status updated.",
        },
    )
