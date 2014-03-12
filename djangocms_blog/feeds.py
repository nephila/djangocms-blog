# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from .models import Post


class LatestEntriesFeed(Feed):

    def link(self):
        return reverse('djangocms_blog:posts-latest')

    def title(self):
        return _('Blog articles on %(site_name)s') % {'site_name': Site.objects.get_current().name}

    def items(self, obj):
        return Post.objects.published().order_by('-date_published')[:10]

    def item_title(self, item):
        return item.safe_translation_getter('title')

    def item_description(self, item):
        return item.safe_translation_getter('abstract')


class TagFeed(LatestEntriesFeed):

    def get_object(self, request, tag):
        return tag

    def items(self, obj):
        return Post.objects.published().filter(tags__slug=obj)[:10]
