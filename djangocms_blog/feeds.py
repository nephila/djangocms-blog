# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from aldryn_apphooks_config.utils import get_app_instance
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.six import BytesIO
from django.utils.text import normalize_newlines
from django.utils.translation import get_language_from_request, ugettext as _
from lxml import etree

from djangocms_blog.settings import get_setting
from djangocms_blog.views import PostDetailView

from .models import Post

try:
    import HTMLParser

    h = HTMLParser.HTMLParser()
except ImportError:
    from html.parser import HTMLParser

    h = HTMLParser()


class LatestEntriesFeed(Feed):
    feed_type = Rss201rev2Feed
    feed_items_number = get_setting('FEED_LATEST_ITEMS')

    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.namespace, self.config = get_app_instance(request)
        return super(LatestEntriesFeed, self).__call__(request, *args, **kwargs)

    def link(self):
        return reverse('%s:posts-latest' % self.namespace, current_app=self.namespace)

    def title(self):
        return Site.objects.get_current().name

    def description(self):
        return _('Blog articles on %(site_name)s') % {'site_name': Site.objects.get_current().name}

    def items(self, obj=None):
        return Post.objects.namespace(
            self.namespace
        ).published().order_by('-date_published')[:self.feed_items_number]

    def item_title(self, item):
        return mark_safe(item.safe_translation_getter('title'))

    def item_description(self, item):
        if item.app_config.use_abstract:
            return mark_safe(item.safe_translation_getter('abstract'))
        return mark_safe(item.safe_translation_getter('post_text'))

    def item_updateddate(self, item):
        return item.date_modified

    def item_pubdate(self, item):
        return item.date_published

    def item_guid(self, item):
        return item.guid

    def item_author_name(self, item):
        return item.get_author_name()

    def item_author_url(self, item):
        return item.get_author_url()


class TagFeed(LatestEntriesFeed):
    feed_items_number = get_setting('FEED_TAGS_ITEMS')

    def get_object(self, request, tag):
        return tag  # pragma: no cover

    def items(self, obj=None):
        return Post.objects.published().filter(tags__slug=obj)[:self.feed_items_number]


class FBInstantFeed(Rss201rev2Feed):
    date_format = '%Y-%m-%dT%H:%M:%S%z'

    def rss_attributes(self):
        return {
            'version': self._version,
            'xmlns:content': 'http://purl.org/rss/1.0/modules/content/'
        }

    def add_root_elements(self, handler):
        handler.addQuickElement('title', self.feed['title'])
        handler.addQuickElement('link', self.feed['link'])
        handler.addQuickElement('description', self.feed['description'])
        if self.feed['language'] is not None:
            handler.addQuickElement('language', self.feed['language'])
        for cat in self.feed['categories']:
            handler.addQuickElement('category', cat)
        if self.feed['feed_copyright'] is not None:
            handler.addQuickElement('copyright', self.feed['feed_copyright'])
        handler.addQuickElement(
            'lastBuildDate', self.latest_post_date().strftime(self.date_format)
        )
        if self.feed['ttl'] is not None:
            handler.addQuickElement('ttl', self.feed['ttl'])

    def add_item_elements(self, handler, item):
        super(FBInstantFeed, self).add_item_elements(handler, item)
        if item['author']:
            handler.addQuickElement('author', item['author'])
        if item['date_pub'] is not None:
            handler.addQuickElement('pubDate', item['date_pub'].strftime(self.date_format))
        if item['date_mod'] is not None:
            handler.addQuickElement('modDate', item['date_mod'].strftime(self.date_format))

        handler.startElement('description', {})
        handler._write('<![CDATA[{0}]]>'.format(
            h.unescape(normalize_newlines(force_text(item['abstract'])).replace('\n', ' ')))
        )
        handler.endElement('description')
        handler.startElement('content:encoded', {})
        handler._write('<![CDATA[')
        handler._write('<!doctype html>')
        handler._write(h.unescape(force_text(item['content'])))
        handler._write(']]>')
        handler.endElement('content:encoded')


class FBInstantArticles(LatestEntriesFeed):
    feed_type = FBInstantFeed
    feed_items_number = get_setting('FEED_INSTANT_ITEMS')

    def items(self, obj=None):
        return Post.objects.namespace(
            self.namespace
        ).published().order_by('-date_modified')[:self.feed_items_number]

    def _clean_html(self, content):
        body = BytesIO(content)
        document = etree.iterparse(body, html=True)
        for a, e in document:
            if not (e.text and e.text.strip()) and len(e) == 0 and e.tag == 'p':
                e.getparent().remove(e)
            if e.tag in ('h3', 'h4', 'h5', 'h6') and 'op-kicker' not in e.attrib.get('class', ''):
                e.tag = 'h2'
        return etree.tostring(document.root)

    def item_extra_kwargs(self, item):
        if not item:
            return {}
        language = get_language_from_request(self.request, check_path=True)
        key = item.get_cache_key(language, 'feed')
        content = cache.get(key)
        if not content:
            view = PostDetailView.as_view(instant_article=True)
            response = view(self.request, slug=item.safe_translation_getter('slug'))
            response.render()
            content = self._clean_html(response.content)
            cache.set(key, content, timeout=get_setting('FEED_CACHE_TIMEOUT'))
        if item.app_config.use_abstract:
            abstract = strip_tags(item.safe_translation_getter('abstract'))
        else:
            abstract = strip_tags(item.safe_translation_getter('post_text'))
        return {
            'author': item.get_author_name(),
            'content': content,
            'date': item.date_modified,
            'date_pub': item.date_modified,
            'date_mod': item.date_modified,
            'abstract': abstract
        }

    def item_categories(self, item):
        return [category.safe_translation_getter('name') for category in item.categories.all()]

    def item_author_name(self, item):
        return ''

    def item_author_url(self, item):
        return ''

    def item_description(self, item):
        return None

    def item_pubdate(self, item):
        return None
