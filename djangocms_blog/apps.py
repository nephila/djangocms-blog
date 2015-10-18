# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PageMetaConfig(AppConfig):
    name = 'djangocms_page_meta'
    verbose_name = _('django CMS Page Meta')
