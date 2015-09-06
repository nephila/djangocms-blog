# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os.path
import re

from cms.api import add_plugin
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from taggit.models import Tag

from djangocms_blog.models import BlogCategory

from . import BaseTest


class PluginTest(BaseTest):

    def test_plugin_latest(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].tags.add('tag 1')
        posts[0].publish = True
        posts[0].save()
        ph = pages[0].placeholders.get(slot='content')

        plugin = add_plugin(ph, 'BlogLatestEntriesPlugin', language='en', app_config=self.app_config_1)
        tag = Tag.objects.get(slug='tag-1')
        plugin.tags.add(tag)

        context = self.get_plugin_context(pages[0], 'en', plugin, edit=True)
        rendered = plugin.render_plugin(context, ph)
        try:
            self.assertTrue(rendered.find('cms_plugin-djangocms_blog-post-abstract-1') > -1)
        except AssertionError:
            self.assertTrue(rendered.find('cms-plugin-djangocms_blog-post-abstract-1') > -1)
        self.assertTrue(rendered.find(reverse('djangocms_blog:posts-tagged', kwargs={'tag': tag.slug})) > -1)
        self.assertTrue(rendered.find('<p>first line</p>') > -1)
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find(posts[0].get_absolute_url()) > -1)

        category_2 = BlogCategory.objects.create(name='category 2', app_config=self.app_config_1)
        category_2.set_current_language('it', initialize=True)
        category_2.name = 'categoria 2'
        category_2.save()
        category_2.set_current_language('en')
        posts[1].categories.add(category_2)
        plugin = add_plugin(ph, 'BlogLatestEntriesPlugin', language='en', app_config=self.app_config_1)
        plugin.categories.add(category_2)

        context = self.get_plugin_context(pages[0], 'en', plugin, edit=True)
        rendered = plugin.render_plugin(context, ph)
        try:
            self.assertTrue(rendered.find('cms_plugin-djangocms_blog-post-abstract-2') > -1)
        except AssertionError:
            self.assertTrue(rendered.find('cms-plugin-djangocms_blog-post-abstract-2') > -1)
        self.assertTrue(rendered.find(reverse('djangocms_blog:posts-category', kwargs={'category': category_2.slug})) > -1)
        self.assertTrue(rendered.find('<p>second post first line</p>') > -1)
        self.assertTrue(rendered.find('<article id="post-second-post"') > -1)
        self.assertTrue(rendered.find(posts[1].get_absolute_url()) > -1)

    def test_plugin_authors(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].publish = True
        posts[0].save()
        posts[1].publish = True
        posts[1].save()
        ph = pages[0].placeholders.get(slot='content')
        plugin = add_plugin(ph, 'BlogAuthorPostsPlugin', language='en', app_config=self.app_config_1)
        plugin.authors.add(self.user)

        context = self.get_plugin_context(pages[0], 'en', plugin, edit=True)
        rendered = plugin.render_plugin(context, ph)
        self.assertTrue(rendered.find(reverse('djangocms_blog:posts-author', kwargs={'username': self.user.get_username()})) > -1)
        self.assertTrue(rendered.find('2 articles') > -1)

    def test_plugin_tags(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].tags.add('tag 1', 'tag 2', 'test tag')
        posts[0].publish = True
        posts[0].save()
        posts[1].tags.add('test tag', 'another tag')
        posts[1].publish = True
        posts[1].save()
        ph = pages[0].placeholders.get(slot='content')
        plugin = add_plugin(ph, 'BlogTagsPlugin', language='en', app_config=self.app_config_1)
        context = self.get_plugin_context(pages[0], 'en', plugin, edit=True)
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
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].publish = True
        posts[0].save()
        posts[1].publish = True
        posts[1].save()
        ph = pages[0].placeholders.get(slot='content')
        plugin = add_plugin(ph, 'BlogCategoryPlugin', language='en', app_config=self.app_config_1)
        plugin_class = plugin.get_plugin_class_instance()
        context = self.get_plugin_context(pages[0], 'en', plugin, edit=True)
        context = plugin_class.render(context, plugin, ph)
        self.assertTrue(context['categories'])
        self.assertEqual(list(context['categories']), [self.category_1])

    def test_blog_archive_plugin(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].publish = True
        posts[0].save()
        posts[1].publish = True
        posts[1].save()
        ph = pages[0].placeholders.get(slot='content')
        plugin = add_plugin(ph, 'BlogArchivePlugin', language='en', app_config=self.app_config_1)
        plugin_class = plugin.get_plugin_class_instance()

        context = self.get_plugin_context(pages[0], 'en', plugin, edit=True)
        context = plugin_class.render(context, plugin, ph)
        self.assertEqual(context['dates'][0]['date'].date(), now().replace(year=now().year, month=now().month, day=1).date())
        self.assertEqual(context['dates'][0]['count'], 2)

        posts[1].publish = False
        posts[1].save()
        context = plugin_class.render(context, plugin, ph)
        self.assertEqual(context['dates'][0]['date'].date(), now().replace(year=now().year, month=now().month, day=1).date())
        self.assertEqual(context['dates'][0]['count'], 1)

    def test_templates(self):
        posts = self.get_posts()
        pages = self.get_pages()

        ph = pages[0].placeholders.get(slot='content')
        plugin = add_plugin(ph, 'BlogLatestEntriesPlugin', language='en', app_config=self.app_config_1)

        context = self.get_plugin_context(pages[0], 'en', plugin)
        plugin_class = plugin.get_plugin_class_instance()
        self.assertEqual(plugin_class.get_render_template(context, plugin, ph), os.path.join('djangocms_blog', plugin_class.base_render_template))

        self.app_config_1.app_data.config.template_prefix = 'whatever'
        self.app_config_1.save()
        self.assertEqual(plugin_class.get_render_template(context, plugin, ph), os.path.join('whatever', plugin_class.base_render_template))
        self.app_config_1.app_data.config.template_prefix = ''
        self.app_config_1.save()

