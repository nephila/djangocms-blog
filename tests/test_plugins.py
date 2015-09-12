# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import re

from cms.api import add_plugin
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from taggit.models import Tag

from djangocms_blog.models import BlogCategory

from . import BaseTest


class PluginTest(BaseTest):

    def test_plugin_latest(self):
        page1, page2 = self.get_pages()
        post1 = self._get_post(self.data['en'][0])
        post2 = self._get_post(self.data['en'][1])
        post1.tags.add('tag 1')
        post1.publish = True
        post1.save()
        ph = page1.placeholders.get(slot='content')

        plugin = add_plugin(ph, 'BlogLatestEntriesPlugin', language='en')
        tag = Tag.objects.get(slug='tag-1')
        plugin.tags.add(tag)

        context = self.get_plugin_context(page1, 'en', plugin, edit=True)
        rendered = plugin.render_plugin(context, ph)
        self.assertTrue(rendered.find('cms_plugin-djangocms_blog-post-abstract-1') > -1)
        self.assertTrue(rendered.find(reverse('djangocms_blog:posts-tagged', kwargs={'tag': tag.slug})) > -1)
        self.assertTrue(rendered.find('<p>first line</p>') > -1)
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find(post1.get_absolute_url()) > -1)

        category_2 = BlogCategory.objects.create(name=u'category 2')
        category_2.set_current_language('it', initialize=True)
        category_2.name = u'categoria 2'
        category_2.save()
        category_2.set_current_language('en')
        post2.categories.add(category_2)
        plugin = add_plugin(ph, 'BlogLatestEntriesPlugin', language='en')
        plugin.categories.add(category_2)

        context = self.get_plugin_context(page1, 'en', plugin, edit=True)
        rendered = plugin.render_plugin(context, ph)
        self.assertTrue(rendered.find('cms_plugin-djangocms_blog-post-abstract-2') > -1)
        self.assertTrue(rendered.find(reverse('djangocms_blog:posts-category', kwargs={'category': category_2.slug})) > -1)
        self.assertTrue(rendered.find('<p>second post first line</p>') > -1)
        self.assertTrue(rendered.find('<article id="post-second-post"') > -1)
        self.assertTrue(rendered.find(post2.get_absolute_url()) > -1)

    def test_plugin_authors(self):
        page1, page2 = self.get_pages()
        post1 = self._get_post(self.data['en'][0])
        post2 = self._get_post(self.data['en'][1])
        post1.publish = True
        post1.save()
        post2.publish = True
        post2.save()
        ph = page1.placeholders.get(slot='content')
        plugin = add_plugin(ph, 'BlogAuthorPostsPlugin', language='en')
        plugin.authors.add(self.user)

        context = self.get_plugin_context(page1, 'en', plugin, edit=True)
        rendered = plugin.render_plugin(context, ph)
        self.assertTrue(rendered.find(reverse('djangocms_blog:posts-author', kwargs={'username': self.user.get_username()})) > -1)
        self.assertTrue(rendered.find('2 articles') > -1)

    def test_plugin_tags(self):
        page1, page2 = self.get_pages()
        post1 = self._get_post(self.data['en'][0])
        post2 = self._get_post(self.data['en'][1])
        post1.tags.add('tag 1', 'tag 2', 'test tag')
        post1.publish = True
        post1.save()
        post2.tags.add('test tag', 'another tag')
        post2.publish = True
        post2.save()
        ph = page1.placeholders.get(slot='content')
        plugin = add_plugin(ph, 'BlogTagsPlugin', language='en')
        context = self.get_plugin_context(page1, 'en', plugin, edit=True)
        rendered = plugin.render_plugin(context, ph)
        for tag in Tag.objects.all():
            self.assertTrue(rendered.find(reverse('djangocms_blog:posts-tagged', kwargs={'tag': tag.slug})) > -1)
            if tag.slug == 'test-tag':
                rf = '\s+%s\s+<span>\(\s+%s articles' % (tag.name, 2)
            else:
                rf = '\s+%s\s+<span>\(\s+%s article' % (tag.name, 1)
            rx = re.compile(rf)
            self.assertEqual(len(rx.findall(rendered)), 1)

    def test_blog_category_plugin(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()
        post1.publish = True
        post1.save()
        post2.publish = True
        post2.save()
        ph = page1.placeholders.get(slot='content')
        plugin = add_plugin(ph, 'BlogCategoryPlugin', language='en')
        plugin_class = plugin.get_plugin_class_instance()
        context = self.get_plugin_context(page1, 'en', plugin, edit=True)
        context = plugin_class.render(context, plugin, ph)
        self.assertTrue(context['categories'])
        self.assertEqual(list(context['categories']), [self.category_1])

    def test_blog_archive_plugin(self):
        page1, page2 = self.get_pages()
        post1, post2 = self.get_posts()
        post1.publish = True
        post1.save()
        post2.publish = True
        post2.save()
        ph = page1.placeholders.get(slot='content')
        plugin = add_plugin(ph, 'BlogArchivePlugin', language='en')
        plugin_class = plugin.get_plugin_class_instance()

        context = self.get_plugin_context(page1, 'en', plugin, edit=True)
        context = plugin_class.render(context, plugin, ph)
        self.assertEqual(context['dates'][0]['date'].date(), now().replace(year=now().year, month=now().month, day=1).date())
        self.assertEqual(context['dates'][0]['count'], 2)

        post2.publish = False
        post2.save()
        context = plugin_class.render(context, plugin, ph)
        self.assertEqual(context['dates'][0]['date'].date(), now().replace(year=now().year, month=now().month, day=1).date())
        self.assertEqual(context['dates'][0]['count'], 1)
