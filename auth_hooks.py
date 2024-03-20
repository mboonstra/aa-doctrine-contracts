"""Define hooks for Alliance Auth like the sidebar menu entry."""

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class DoctrineContractsMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        super().__init__(
            "doctrinecontracts",
            "fa fa-space-shuttle fa-fw",
            "doctrinecontracts:index",
            navactive=["doctrinecontracts:"],
        )

    def render(self, request):
        if request.user.has_perm("doctrinecontracts.basic_access") or True:
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return DoctrineContractsMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "doctrinecontracts", "doctrinecontracts/")
