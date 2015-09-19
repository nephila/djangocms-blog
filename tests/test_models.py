# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from copy import deepcopy

import parler
from cms.api import add_plugin
from cms.utils.copy_plugins import copy_plugins_to
from cms.utils.plugins import downcast_plugins
from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.utils.translation import get_language, override
from djangocms_helper.utils import CMS_30
from taggit.models import Tag

from djangocms_blog.models import Post
from djangocms_blog.settings import get_setting

from . import BaseTest


class AdminTest(BaseTest):

    def setUp(self):
        super(AdminTest, self).setUp()
        admin.autodiscover()

    def test_admin_fieldsets(self):
        post_admin = admin.site._registry[Post]
        request = self.get_page_request('/', self.user_staff, r'/en/blog/?app_config=%s' % self.app_config_1.pk, edit=False)

        # Use placeholder
        self.app_config_1.app_data.config.use_placeholder = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse('post_text' in fsets[0][1]['fields'])

        self.app_config_1.app_data.config.use_placeholder = False
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue('post_text' in fsets[0][1]['fields'])

        self.app_config_1.app_data.config.use_placeholder = True
        self.app_config_1.save()

        # Use abstract
        self.app_config_1.app_data.config.use_abstract = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue('abstract' in fsets[0][1]['fields'])

        self.app_config_1.app_data.config.use_abstract = False
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse('abstract' in fsets[0][1]['fields'])

        self.app_config_1.app_data.config.use_abstract = True
        self.app_config_1.save()

        with self.settings(BLOG_MULTISITE=True):
            fsets = post_admin.get_fieldsets(request)
            self.assertTrue('sites' in fsets[1][1]['fields'][0])
        with self.settings(BLOG_MULTISITE=False):
            fsets = post_admin.get_fieldsets(request)
            self.assertFalse('sites' in fsets[1][1]['fields'][0])

        request = self.get_page_request('/', self.user, r'/en/blog/?app_config=%s' % self.app_config_1.pk, edit=False)
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue('author' in fsets[1][1]['fields'][0])

    def test_admin_auto_author(self):
        pages = self.get_pages()
        data = deepcopy(self._post_data[0]['en'])

        with self.login_user_context(self.user):
            self.app_config_1.app_data.config.set_author = True
            self.app_config_1.save()
            data['date_published_0'] = now().strftime('%Y-%m-%d')
            data['date_published_1'] = now().strftime('%H:%M:%S')
            data['categories'] = self.category_1.pk
            data['app_config'] = self.app_config_1.pk
            request = self.post_request(pages[0], 'en', user=self.user, data=data, path=r'/en/blog/?app_config=%s' % self.app_config_1.pk)
            msg_mid = MessageMiddleware()
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            response = post_admin.add_view(request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Post.objects.count(), 1)
            self.assertEqual(Post.objects.get(translations__slug='first-post').author_id, request.user.pk)

            self.app_config_1.app_data.config.set_author = False
            self.app_config_1.save()
            data = deepcopy(self._post_data[1]['en'])
            data['date_published_0'] = now().strftime('%Y-%m-%d')
            data['date_published_1'] = now().strftime('%H:%M:%S')
            data['categories'] = self.category_1.pk
            data['app_config'] = self.app_config_1.pk
            request = self.post_request(pages[0], 'en', user=self.user, data=data, path=r'/en/blog/?app_config=%s' % self.app_config_1.pk)
            msg_mid = MessageMiddleware()
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            response = post_admin.add_view(request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Post.objects.count(), 2)
            self.assertEqual(Post.objects.get(translations__slug='second-post').author_id, None)

            with self.settings(BLOG_AUTHOR_DEFAULT='staff'):
                self.app_config_1.app_data.config.set_author = True
                self.app_config_1.save()
                data = deepcopy(self._post_data[2]['en'])
                data['date_published_0'] = now().strftime('%Y-%m-%d')
                data['date_published_1'] = now().strftime('%H:%M:%S')
                data['categories'] = self.category_1.pk
                data['app_config'] = self.app_config_1.pk
                request = self.post_request(pages[0], 'en', user=self.user, data=data, path=r'/en/blog/?app_config=%s' % self.app_config_1.pk)
                msg_mid = MessageMiddleware()
                msg_mid.process_request(request)
                post_admin = admin.site._registry[Post]
                response = post_admin.add_view(request)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(Post.objects.count(), 3)
                self.assertEqual(Post.objects.get(translations__slug='third-post').author.username, 'staff')

    def test_admin_post_text(self):
        pages = self.get_pages()
        post = self._get_post(self._post_data[0]['en'])

        with self.login_user_context(self.user):
            with self.settings(BLOG_USE_PLACEHOLDER=False):
                data = {'post_text': 'ehi text', 'title': 'some title'}
                request = self.post_request(pages[0], 'en', user=self.user, data=data, path='/en/?edit_fields=post_text')
                msg_mid = MessageMiddleware()
                msg_mid.process_request(request)
                post_admin = admin.site._registry[Post]
                response = post_admin.edit_field(request, post.pk, 'en')
                #print(response.content.decode('utf-8'))
                self.assertEqual(response.status_code, 200)
                modified_post = Post.objects.language('en').get(pk=post.pk)
                self.assertEqual(modified_post.safe_translation_getter('post_text'), data['post_text'])


class ModelsTest(BaseTest):

    def test_model_attributes(self):
        post = self._get_post(self._post_data[0]['en'])
        post = self._get_post(self._post_data[0]['it'], post, 'it')
        post.main_image = self.img
        post.save()
        post.set_current_language('en')
        meta_en = post.as_meta()
        self.assertEqual(meta_en.og_type, get_setting('FB_TYPE'))
        self.assertEqual(meta_en.title, post.title)
        self.assertTrue(meta_en.url.endswith(post.get_absolute_url()))
        self.assertEqual(meta_en.description, post.meta_description)
        self.assertEqual(meta_en.keywords, post.meta_keywords.split(','))
        self.assertEqual(meta_en.published_time, post.date_published)
        post.set_current_language('it')
        meta_it = post.as_meta()
        self.assertEqual(meta_it.title, post.title)
        self.assertTrue(meta_it.url.endswith(post.get_absolute_url()))
        self.assertNotEqual(meta_it.title, meta_en.title)
        self.assertEqual(meta_it.description, post.meta_description)

        with override('en'):
            post.set_current_language(get_language())
            kwargs = {'year': post.date_published.year,
                      'month': '%02d' % post.date_published.month,
                      'day': '%02d' % post.date_published.day,
                      'slug': post.safe_translation_getter('slug', any_language=get_language())}
            url_en = reverse('djangocms_blog:post-detail', kwargs=kwargs)
            self.assertEqual(url_en, post.get_absolute_url())

        with override('it'):
            post.set_current_language(get_language())
            kwargs = {'year': post.date_published.year,
                      'month': '%02d' % post.date_published.month,
                      'day': '%02d' % post.date_published.day,
                      'slug': post.safe_translation_getter('slug', any_language=get_language())}
            url_it = reverse('djangocms_blog:post-detail', kwargs=kwargs)
            self.assertEqual(url_it, post.get_absolute_url())
            self.assertNotEqual(url_it, url_en)

            self.assertEqual(post.get_full_url(), 'http://example.com%s' % url_it)
        self.assertEqual(post.get_image_full_url(), 'http://example.com%s' % post.main_image.url)

        self.assertEqual(post.thumbnail_options(), get_setting('IMAGE_THUMBNAIL_SIZE'))
        self.assertEqual(post.full_image_options(), get_setting('IMAGE_FULL_SIZE'))

        post.main_image_thumbnail = self.thumb_1
        post.main_image_full = self.thumb_2
        self.assertEqual(post.thumbnail_options(), {
            'size': (100, 100),
            'width': 100, 'height': 100,
            'crop': True,
            'upscale': False
        })
        self.assertEqual(post.full_image_options(), {
            'size': (200, 200),
            'width': 200, 'height': 200,
            'crop': False,
            'upscale': False
        })

        post.set_current_language('en')
        post.meta_title = 'meta title'
        self.assertEqual(post.get_title(), 'meta title')

    def test_manager(self):
        post1 = self._get_post(self._post_data[0]['en'])
        post2 = self._get_post(self._post_data[1]['en'])

        # default queryset, published and unpublished posts
        months = Post.objects.get_months()
        for data in months:
            self.assertEqual(data['date'].date(), now().replace(year=now().year, month=now().month, day=1).date())
            self.assertEqual(data['count'], 2)

        # custom queryset, only published
        post1.publish = True
        post1.save()
        months = Post.objects.get_months(Post.objects.published())
        for data in months:
            self.assertEqual(data['date'].date(), now().replace(year=now().year, month=now().month, day=1).date())
            self.assertEqual(data['count'], 1)

        self.assertEqual(len(Post.objects.available()), 1)

        # If post is published but publishing date is in the future
        post2.date_published = now().replace(year=now().year + 1, month=now().month, day=1)
        post2.publish = True
        post2.save()
        self.assertEqual(len(Post.objects.available()), 2)
        self.assertEqual(len(Post.objects.published()), 1)
        self.assertEqual(len(Post.objects.archived()), 0)

        # If post is published but end publishing date is in the past
        post2.date_published = now().replace(year=now().year - 2, month=now().month, day=1)
        post2.date_published_end = now().replace(year=now().year - 1, month=now().month, day=1)
        post2.save()
        self.assertEqual(len(Post.objects.available()), 2)
        self.assertEqual(len(Post.objects.published()), 1)
        self.assertEqual(len(Post.objects.archived()), 1)

        # counting with language fallback enabled
        self._get_post(self._post_data[0]['it'], post1, 'it')
        self.assertEqual(len(Post.objects.filter_by_language('it')), 2)

        # No fallback
        parler.appsettings.PARLER_LANGUAGES['default']['hide_untranslated'] = True
        for index, lang in enumerate(parler.appsettings.PARLER_LANGUAGES[Site.objects.get_current().pk]):
            parler.appsettings.PARLER_LANGUAGES[Site.objects.get_current().pk][index]['hide_untranslated'] = True
        self.assertEqual(len(Post.objects.filter_by_language('it')), 1)
        parler.appsettings.PARLER_LANGUAGES['default']['hide_untranslated'] = False
        for index, lang in enumerate(parler.appsettings.PARLER_LANGUAGES[Site.objects.get_current().pk]):
            parler.appsettings.PARLER_LANGUAGES[Site.objects.get_current().pk][index]['hide_untranslated'] = False

    def test_tag_cloud(self):
        post1 = self._get_post(self._post_data[0]['en'])
        post2 = self._get_post(self._post_data[1]['en'])
        post1.tags.add('tag 1', 'tag 2', 'tag 3', 'tag 4')
        post1.save()
        post2.tags.add('tag 6', 'tag 2', 'tag 5', 'tag 8')
        post2.save()

        self.assertEqual(len(Post.objects.tag_cloud()), 0)

        tags = []
        for tag in Tag.objects.all():
            if tag.slug == 'tag-2':
                tag.count = 2
            else:
                tag.count = 1
            tags.append(tag)

        self.assertEqual(Post.objects.tag_cloud(published=True), [])
        self.assertEqual(set(Post.objects.tag_cloud(published=False)), set(tags))

        tags_1 = []
        for tag in Tag.objects.all():
            if tag.slug == 'tag-2':
                tag.count = 2
                tags_1.append(tag)
            elif tag.slug in ('tag-1', 'tag-3', 'tag-4'):
                tag.count = 1
                tags_1.append(tag)

        post1.publish = True
        post1.save()
        self.assertEqual(set(Post.objects.tag_cloud()), set(tags_1))
        self.assertEqual(set(Post.objects.tag_cloud(published=False)), set(tags))

    def test_plugin_latest(self):
        post1 = self._get_post(self._post_data[0]['en'])
        self._get_post(self._post_data[1]['en'])
        post1.tags.add('tag 1')
        post1.save()
        request = self.get_page_request('/', AnonymousUser(), r'/en/blog/', edit=False)
        request_auth = self.get_page_request('/', self.user_staff, r'/en/blog/', edit=False)
        request_edit = self.get_page_request('/', self.user_staff, r'/en/blog/', edit=True)
        plugin = add_plugin(post1.content, 'BlogLatestEntriesPlugin', language='en', app_config=self.app_config_1)
        tag = Tag.objects.get(slug='tag-1')
        plugin.tags.add(tag)
        # unauthenticated users get no post
        self.assertEqual(len(plugin.get_posts(request)), 0)
        # staff users not in edit mode get no post
        self.assertEqual(len(plugin.get_posts(request_auth)), 0)
        # staff users in edit mode get the post
        self.assertEqual(len(plugin.get_posts(request_edit)), 1)

        post1.publish = True
        post1.save()
        self.assertEqual(len(plugin.get_posts(request)), 1)

    def test_copy_plugin_latest(self):
        post1 = self._get_post(self._post_data[0]['en'])
        post2 = self._get_post(self._post_data[1]['en'])
        tag1 = Tag.objects.create(name='tag 1')
        tag2 = Tag.objects.create(name='tag 2')
        plugin = add_plugin(post1.content, 'BlogLatestEntriesPlugin', language='en', app_config=self.app_config_1)
        plugin.tags.add(tag1)
        plugin.tags.add(tag2)
        if CMS_30:
            plugins = list(post1.content.cmsplugin_set.filter(language='en').order_by('tree_id', 'level', 'position'))
        else:
            plugins = list(post1.content.cmsplugin_set.filter(language='en').order_by('path', 'depth', 'position'))
        copy_plugins_to(plugins, post2.content)
        new = downcast_plugins(post2.content.cmsplugin_set.all())
        self.assertEqual(set(new[0].tags.all()), set([tag1, tag2]))
        self.assertEqual(set(new[0].tags.all()), set(plugin.tags.all()))

    def test_plugin_author(self):
        post1 = self._get_post(self._post_data[0]['en'])
        post2 = self._get_post(self._post_data[1]['en'])
        request = self.get_page_request('/', AnonymousUser(), r'/en/blog/', edit=False)
        plugin = add_plugin(post1.content, 'BlogAuthorPostsPlugin', language='en', app_config=self.app_config_1)
        plugin.authors.add(self.user)
        self.assertEqual(len(plugin.get_posts(request)), 0)
        self.assertEqual(plugin.get_authors()[0].count, 0)

        post1.publish = True
        post1.save()
        self.assertEqual(len(plugin.get_posts(request)), 1)
        self.assertEqual(plugin.get_authors()[0].count, 1)

        post2.publish = True
        post2.save()
        self.assertEqual(len(plugin.get_posts(request)), 2)
        self.assertEqual(plugin.get_authors()[0].count, 2)

    def test_copy_plugin_author(self):
        post1 = self._get_post(self._post_data[0]['en'])
        post2 = self._get_post(self._post_data[1]['en'])
        plugin = add_plugin(post1.content, 'BlogAuthorPostsPlugin', language='en', app_config=self.app_config_1)
        plugin.authors.add(self.user)
        if CMS_30:
            plugins = list(post1.content.cmsplugin_set.filter(language='en').order_by('tree_id', 'level', 'position'))
        else:
            plugins = list(post1.content.cmsplugin_set.filter(language='en').order_by('path', 'depth', 'position'))
        copy_plugins_to(plugins, post2.content)
        new = downcast_plugins(post2.content.cmsplugin_set.all())
        self.assertEqual(set(new[0].authors.all()), set([self.user]))

    def test_multisite(self):
        with override('en'):
            post1 = self._get_post(self._post_data[0]['en'], sites=(self.site_1,))
            post2 = self._get_post(self._post_data[1]['en'], sites=(self.site_2,))
            post3 = self._get_post(self._post_data[2]['en'], sites=(self.site_2, self.site_1))

            self.assertEqual(len(Post.objects.all()), 3)
            with self.settings(**{'SITE_ID': self.site_1.pk}):
                self.assertEqual(len(Post.objects.all().on_site()), 2)
                self.assertEqual(set(list(Post.objects.all().on_site())), set([post1, post3]))
            with self.settings(**{'SITE_ID': self.site_2.pk}):
                self.assertEqual(len(Post.objects.all().on_site()), 2)
                self.assertEqual(set(list(Post.objects.all().on_site())), set([post2, post3]))
