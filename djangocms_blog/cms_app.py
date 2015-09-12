# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

from .menu import BlogCategoryMenu


class BlogApp(CMSApp):
    name = _('Blog')
    urls = ['djangocms_blog.urls']
    app_name = 'djangocms_blog'
    menus = [BlogCategoryMenu]

apphook_pool.register(BlogApp)
