# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib.sitemaps import Sitemap

from ..models import Post


class BlogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.date_modified
