from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


@apphook_pool.register
class ShareLinksApphook(CMSApp):
    app_name = "share_links"
    name = "Share Links"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["share_links.urls"]
