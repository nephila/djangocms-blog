from cms.app_base import CMSAppConfig

from .models import Post
from .rendering import render_post_content


class BlogCMSConfig(CMSAppConfig):
    cms_enabled = True
    cms_toolbar_enabled_models = [(Post, render_post_content)]
