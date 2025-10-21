"""Hook into Alliance Auth"""

# Django
from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from autosrp import urls

class AutoSRPMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""
    def __init__(self):
        MenuItemHook.__init__(
            self,
            _("SRP"),
            "fas fa-cube fa-fw",
            "autosrp:user_landing",
            navactive=["autosrp:"],
        )

    def render(self, request):
        """Render the menu item"""
        if request.user.has_perm("autosrp.basic_access"):
            return MenuItemHook.render(self, request)

        return ""

@hooks.register("menu_item_hook")
def register_menu():
    """Register the menu item"""
    return AutoSRPMenuItem()

@hooks.register("url_hook")
def register_urls():
    """Register app urls"""
    return UrlHook(urls, "autosrp", r"^autosrp/")
