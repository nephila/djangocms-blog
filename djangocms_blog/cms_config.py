from django.apps import apps
from django.conf import settings

from cms.app_base import CMSAppConfig

from .models import Post
from .views import PostDetailView


class AliasCMSConfig(CMSAppConfig):
    cms_enabled = True
    cms_toolbar_enabled_models = [(Post, PostDetailView)]
