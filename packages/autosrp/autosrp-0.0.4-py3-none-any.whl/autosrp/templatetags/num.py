from decimal import Decimal
from django import template

register = template.Library()

@register.filter
def percent_of(amount, pct):
    try:
        return (Decimal(amount) * Decimal(pct)) / Decimal("100")
    except Exception:
        return 0
