from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BlogAppConfig(AppConfig):
    name = "djangocms_blog"
    verbose_name = _("django CMS Blog")
