# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LiveBlogAppConfig(AppConfig):
    name = 'djangocms_blog.liveblog'
    verbose_name = _('Liveblog')
