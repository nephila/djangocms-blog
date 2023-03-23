from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _
from djangocms_apphook_setup.base import AutoCMSAppMixin

from .cms_appconfig import BlogConfig
from .cms_menus import BlogCategoryMenu
from .settings import get_setting


@apphook_pool.register
class BlogApp(AutoCMSAppMixin, CMSConfigApp):
    name = _("Blog")
    _urls = [get_setting("URLCONF") if isinstance(get_setting("URLCONF"), str) else get_setting("URLCONF")[0][0]]
    app_name = "djangocms_blog"
    app_config = BlogConfig
    _menus = [BlogCategoryMenu]
    auto_setup = {
        "enabled": get_setting("AUTO_SETUP"),
        "home title": get_setting("AUTO_HOME_TITLE"),
        "page title": get_setting("AUTO_BLOG_TITLE"),
        "namespace": get_setting("AUTO_NAMESPACE"),
        "config_fields": {},
        "config_translated_fields": {
            "app_title": get_setting("AUTO_APP_TITLE"),
            "object_name": get_setting("DEFAULT_OBJECT_NAME"),
        },
    }

    def get_urls(self, page=None, language=None, **kwargs):
        urlconf = get_setting("URLCONF")
        if page is None or not page.application_namespace or isinstance(urlconf, str):
            return [urlconf]  # Single urlconf
        return [getattr(self.app_config.objects.get(namespace=page.application_namespace), "urlconf",
                        get_setting("URLCONF")[0][0])]  # Default if no urlconf is configured

    @property
    def urls(self):
        return self.get_urls()

    @property
    def menus(self):
        return self._menus


BlogApp.setup()
