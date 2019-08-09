# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BlogAppConfig(AppConfig):
    name = 'djangocms_blog'
    verbose_name = _('django CMS Blog')
