from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LiveBlogAppConfig(AppConfig):
    name = "djangocms_blog.liveblog"
    verbose_name = _("Liveblog")
