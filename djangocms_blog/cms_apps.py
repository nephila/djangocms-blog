# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from djangocms_apphook_setup.base import AutoCMSAppMixin

from .cms_appconfig import BlogConfig
from .menu import BlogCategoryMenu
from .settings import get_setting


@apphook_pool.register
class BlogApp(AutoCMSAppMixin, CMSConfigApp):
    name = _('Blog')
    urls = ['djangocms_blog.urls']
    app_name = 'djangocms_blog'
    app_config = BlogConfig
    menus = [BlogCategoryMenu]
    auto_setup = {
        'enabled': get_setting('AUTO_SETUP'),
        'home title': get_setting('AUTO_HOME_TITLE'),
        'page title': get_setting('AUTO_BLOG_TITLE'),
        'namespace': get_setting('AUTO_NAMESPACE'),
        'config_fields': {},
        'config_translated_fields': {
            'app_title': get_setting('AUTO_APP_TITLE'),
            'object_name': get_setting('DEFAULT_OBJECT_NAME')
        },
    }


BlogApp.setup()
