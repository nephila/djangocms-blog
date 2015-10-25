# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from djangocms_apphook_setup.base import AutoCMSAppMixin

from .cms_appconfig import BlogConfig
from .menu import BlogCategoryMenu
from .settings import get_setting


class BlogApp(AutoCMSAppMixin, CMSConfigApp):
    name = _('Blog')
    urls = ['djangocms_blog.urls']
    app_name = 'djangocms_blog'
    app_config = BlogConfig
    menus = [BlogCategoryMenu]
    auto_setup = get_setting('AUTO_SETUP')
    auto_app_title = get_setting('AUTO_APP_TITLE')
    auto_home_title = get_setting('AUTO_HOME_TITLE')
    auto_page_title = get_setting('AUTO_BLOG_TITLE')
    auto_namespace = get_setting('AUTO_NAMESPACE')

apphook_pool.register(BlogApp)
BlogApp.setup()
