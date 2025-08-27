from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .cms_menus import BlogCategoryMenu
from .models import BlogConfig
from .settings import get_setting

# from djangocms_apphook_setup.base import AutoCMSAppMixin


@apphook_pool.register
class BlogApp(CMSApp):
    name = _("Blog")
    app_name = "djangocms_blog"
    app_config = BlogConfig
    _urls = [get_setting("URLCONF")]
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
        return [get_setting("URLCONF")]

    @property
    def urls(self):
        return self.get_urls()

    @property
    def menus(self):
        return self._menus

    def get_configs(self):
        return self.app_config.objects.all()

    def get_config(self, namespace):
        try:
            return self.app_config.objects.get(namespace=namespace)
        except ObjectDoesNotExist:
            return None

    def get_config_add_url(self):
        try:
            return reverse(f"admin:{self.app_config._meta.app_label}_{self.app_config._meta.model_name}_add")
        except AttributeError:  # pragma: no cover
            return reverse(f"admin:{self.app_config._meta.app_label}_{self.app_config._meta.module_name}_add")


# BlogApp.setup()
