# -*- coding: utf-8 -*-
from cms.api import add_plugin
from cms.utils.copy_plugins import copy_plugins_to
from cms.utils.plugins import downcast_plugins
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.utils.translation import get_language, activate, override
import parler
from taggit.models import Tag

from djangocms_blog.models import Post
from djangocms_blog import settings


from . import BaseTest


class ModelsTest(BaseTest):

    def test_model_attributes(self):
        post = self._get_post(self.data['en'][0])
        post = self._get_post(self.data['it'][0], post, 'it')
        post.main_image = self.img
        post.save()
        post.set_current_language('en')
        meta_en = post.as_meta()
        self.assertEqual(meta_en.og_type, settings.BLOG_FB_TYPE)
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

        self.assertEqual(post.thumbnail_options(), settings.BLOG_IMAGE_THUMBNAIL_SIZE)
        self.assertEqual(post.full_image_options(), settings.BLOG_IMAGE_FULL_SIZE)

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
        post1 = self._get_post(self.data['en'][0])
        post2 = self._get_post(self.data['en'][1])

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
        post2.date_published = now().replace(year=now().year+1, month=now().month, day=1)
        post2.publish = True
        post2.save()
        self.assertEqual(len(Post.objects.available()), 2)
        self.assertEqual(len(Post.objects.published()), 1)
        self.assertEqual(len(Post.objects.archived()), 0)

        # If post is published but end publishing date is in the past
        post2.date_published = now().replace(year=now().year-2, month=now().month, day=1)
        post2.date_published_end = now().replace(year=now().year-1, month=now().month, day=1)
        post2.save()
        self.assertEqual(len(Post.objects.available()), 2)
        self.assertEqual(len(Post.objects.published()), 1)
        self.assertEqual(len(Post.objects.archived()), 1)

        # counting with language fallback enabled
        post = self._get_post(self.data['it'][0], post1, 'it')
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
        post1 = self._get_post(self.data['en'][0])
        post2 = self._get_post(self.data['en'][1])
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
        post1 = self._get_post(self.data['en'][0])
        post2 = self._get_post(self.data['en'][1])
        post1.tags.add('tag 1')
        post1.save()
        plugin = add_plugin(post1.content, 'BlogLatestEntriesPlugin', language='en')
        tag = Tag.objects.get(slug='tag-1')
        plugin.tags.add(tag)
        self.assertEqual(len(plugin.get_posts()), 0)
        post1.publish = True
        post1.save()
        self.assertEqual(len(plugin.get_posts()), 1)

    def test_copy_plugin_latest(self):
        post1 = self._get_post(self.data['en'][0])
        post2 = self._get_post(self.data['en'][1])
        tag = Tag.objects.create(name='tag 1')
        plugin = add_plugin(post1.content, 'BlogLatestEntriesPlugin', language='en')
        plugin.tags.add(tag)
        plugins = list(post1.content.cmsplugin_set.filter(language='en').order_by('tree_id', 'level', 'position'))
        copy_plugins_to(plugins, post2.content)
        new = downcast_plugins(post2.content.cmsplugin_set.all())
        self.assertEqual(set(new[0].tags.all()), set([tag]))

    def test_plugin_author(self):
        post1 = self._get_post(self.data['en'][0])
        post2 = self._get_post(self.data['en'][1])
        plugin = add_plugin(post1.content, 'BlogAuthorPostsPlugin', language='en')
        plugin.authors.add(self.user)
        self.assertEqual(len(plugin.get_posts()), 0)
        self.assertEqual(plugin.get_authors()[0].count, 0)

        post1.publish = True
        post1.save()
        self.assertEqual(len(plugin.get_posts()), 1)
        self.assertEqual(plugin.get_authors()[0].count, 1)

        post2.publish = True
        post2.save()
        self.assertEqual(len(plugin.get_posts()), 2)
        self.assertEqual(plugin.get_authors()[0].count, 2)

    def test_copy_plugin_author(self):
        post1 = self._get_post(self.data['en'][0])
        post2 = self._get_post(self.data['en'][1])
        plugin = add_plugin(post1.content, 'BlogAuthorPostsPlugin', language='en')
        plugin.authors.add(self.user)
        plugins = list(post1.content.cmsplugin_set.filter(language='en').order_by('tree_id', 'level', 'position'))
        copy_plugins_to(plugins, post2.content)
        new = downcast_plugins(post2.content.cmsplugin_set.all())
        self.assertEqual(set(new[0].authors.all()), set([self.user]))

    def test_multisite(self):
        post1 = self._get_post(self.data['en'][0], sites=(self.site_1,))
        post2 = self._get_post(self.data['en'][1], sites=(self.site_2,))
        post3 = self._get_post(self.data['en'][2], sites=(self.site_2, self.site_1))

        self.assertEqual(len(Post.objects.all()), 3)
        with self.settings(**{'SITE_ID': 1}):
            self.assertEqual(len(Post.objects.all().on_site()), 2)
            self.assertEqual(set(list(Post.objects.all().on_site())), set([post1, post3]))
        with self.settings(**{'SITE_ID': 2}):
            self.assertEqual(len(Post.objects.all().on_site()), 2)
            self.assertEqual(set(list(Post.objects.all().on_site())), set([post2, post3]))
