# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.utils.translation import ugettext_lazy as _

try:
    from django.apps import AppConfig
except ImportError:
    class AppConfig(object):
        pass


class BlogAppConfig(AppConfig):
    name = 'djangocms_blog'
    verbose_name = _('django CMS Blog')
