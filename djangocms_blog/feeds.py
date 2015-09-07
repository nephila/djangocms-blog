# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from aldryn_apphooks_config.utils import get_app_instance
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from .models import Post
from .settings import get_setting


class LatestEntriesFeed(Feed):

    def __call__(self, request, *args, **kwargs):
        self.namespace, self.config = get_app_instance(request)
        return super(LatestEntriesFeed, self).__call__(request, *args, **kwargs)

    def link(self):
        return reverse('%s:posts-latest' % self.namespace, current_app=self.namespace)

    def title(self):
        return _('Blog articles on %(site_name)s') % {'site_name': Site.objects.get_current().name}

    def items(self, obj=None):
        return Post.objects.namespace(self.namespace).published().order_by('-date_published')[:10]

    def item_title(self, item):
        return item.safe_translation_getter('title')

    def item_description(self, item):
        if get_setting('USE_ABSTRACT'):
            return item.safe_translation_getter('abstract')
        return item.safe_translation_getter('post_text')


class TagFeed(LatestEntriesFeed):

    def get_object(self, request, tag):
        return tag  # pragma: no cover

    def items(self, obj=None):
        return Post.objects.published().filter(tags__slug=obj)[:10]
