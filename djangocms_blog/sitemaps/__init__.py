# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.utils import get_language_list
from django.contrib.sitemaps import Sitemap
from django.urls.exceptions import NoReverseMatch
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
            posts = Post.objects.translated(lang).language(lang).published()
            for post in posts:
                # check if the post actually has a url before appending
                # if a post is published but the associated app config is not
                # then this post will not have a url
                try:
                    post.get_absolute_url()
                except NoReverseMatch:
                    # couldn't determine the url of the post so pass on it
                    continue

                items.append(post)

        return items

    def lastmod(self, obj):
        return obj.date_modified
