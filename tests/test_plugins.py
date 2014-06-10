# -*- coding: utf-8 -*-
import re
from cms.api import add_plugin
from django.core.urlresolvers import reverse
from django.template import RequestContext
from taggit.models import Tag

from . import BaseTest


class PluginTest(BaseTest):

    def test_plugin_latest(self):
        page1, page2 = self.get_pages()
        post_1 = self._get_post(self.data['en'][0])
        post_2 = self._get_post(self.data['en'][1])
        post_1.tags.add('tag 1')
        post_1.publish = True
        post_1.save()
        ph = page1.placeholders.get(slot='placeholder')
        plugin = add_plugin(ph, 'BlogLatestEntriesPlugin', language='en')
        tag = Tag.objects.get(slug='tag-1')
        plugin.tags.add(tag)
        request = self.get_page_request(page1, self.user, r'/en/blog/', lang_code='en', edit=True)
        context = RequestContext(request, {})
        rendered = plugin.render_plugin(context, ph)
        self.assertTrue(rendered.find('cms_plugin-djangocms_blog-post-abstract-1') > -1)
        self.assertTrue(rendered.find(reverse('djangocms_blog:posts-tagged', kwargs={'tag': tag.slug})) > -1)
        self.assertTrue(rendered.find('<p>first line</p>') > -1)
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find(post_1.get_absolute_url()) > -1)

    def test_plugin_authors(self):
        page1, page2 = self.get_pages()
        post_1 = self._get_post(self.data['en'][0])
        post_2 = self._get_post(self.data['en'][1])
        post_1.publish = True
        post_1.save()
        post_2.publish = True
        post_2.save()
        ph = page1.placeholders.get(slot='placeholder')
        plugin = add_plugin(ph, 'BlogAuthorPostsPlugin', language='en')
        plugin.authors.add(self.user)
        request = self.get_page_request(page1, self.user, r'/en/blog/', lang_code='en', edit=True)
        context = RequestContext(request, {})
        rendered = plugin.render_plugin(context, ph)
        self.assertTrue(rendered.find(reverse('djangocms_blog:posts-author', kwargs={'username': self.user.username})) > -1)
        self.assertTrue(rendered.find('2 articles') > -1)

    def test_plugin_tags(self):
        page1, page2 = self.get_pages()
        post_1 = self._get_post(self.data['en'][0])
        post_2 = self._get_post(self.data['en'][1])
        post_1.tags.add('tag 1', 'tag 2', 'test tag')
        post_1.publish = True
        post_1.save()
        post_2.tags.add('test tag', 'another tag')
        post_2.publish = True
        post_2.save()
        ph = page1.placeholders.get(slot='placeholder')
        plugin = add_plugin(ph, 'BlogTagsPlugin', language='en')
        request = self.get_page_request(page1, self.user, r'/en/blog/', lang_code='en', edit=True)
        context = RequestContext(request, {})
        rendered = plugin.render_plugin(context, ph).replace("\n", "")
        for tag in Tag.objects.all():
            self.assertTrue(rendered.find(reverse('djangocms_blog:posts-tagged', kwargs={'tag': tag.slug})) > -1)
            if tag.slug == 'test-tag':
                rf = '\s+%s\s+<span>\(\s+%s articles' % (tag.name, 2)
            else:
                rf = '\s+%s\s+<span>\(\s+%s article' % (tag.name, 1)
            rx = re.compile(rf)
            self.assertEqual(len(rx.findall(rendered)), 1)