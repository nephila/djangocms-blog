# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.utils import get_language_list
from django.contrib.sitemaps import Sitemap
from parler.utils.context import smart_override

from ..models import Post
from ..settings import get_setting


class BlogSitemap(Sitemap):

    def priority(self, obj):
        if obj and obj.app_config:
            return obj.app_config.sitemap_priority
        return get_setting('SITEMAP_PRIORITY_DEFAULT')

    def changefreq(self, obj):
        if obj and obj.app_config:
            return obj.app_config.sitemap_changefreq
        return get_setting('SITEMAP_CHANGEFREQ_DEFAULT')

    def location(self, obj):
        with smart_override(obj.get_current_language()):
            return obj.get_absolute_url(obj.get_current_language())

    def items(self):
        items = []
        for lang in get_language_list():
            items.extend(Post.objects.translated(lang).language(lang).published())
        return items

    def lastmod(self, obj):
        return obj.date_modified
