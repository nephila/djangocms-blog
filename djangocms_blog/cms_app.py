# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

from .cms_appconfig import BlogConfig
from .menu import BlogCategoryMenu


class BlogApp(CMSConfigApp):
    name = _('Blog')
    urls = ['djangocms_blog.urls']
    app_name = 'djangocms_blog'
    app_config = BlogConfig
    menus = [BlogCategoryMenu]

apphook_pool.register(BlogApp)
