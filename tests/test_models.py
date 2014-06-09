# -*- coding: utf-8 -*-
from cms.api import add_plugin
from cms.utils.copy_plugins import copy_plugins_to
from cms.utils.plugins import downcast_plugins
from cmsplugin_filer_image.models import ThumbnailOption
from datetime import date
from django.conf import settings as dj_settings
from django.core.urlresolvers import reverse
import parler
from taggit.models import Tag

from djangocms_blog.models import BlogCategory, Post
from djangocms_blog import settings


from . import BaseTest


class ModelsTest(BaseTest):

    data = {
        'it': [
            {'title': u'Primo post', 'abstract': u'<p>prima riga</p>',
             'description': u'Questa è la descrizione', 'keywords': u'keyword1, keyword2',
             'text': u'Testo del post'},
            {'title': u'Secondo post', 'abstract': u'<p>prima riga del secondo post</p>',
             'description': u'Descrizione del secondo post', 'keywords': u'keyword3, keyword4',
             'text': u'Testo del secondo post'},
        ],
        'en': [
            {'title': u'First post', 'abstract': u'<p>first line</p>',
             'description': u'This is the description', 'keywords': u'keyword1, keyword2',
             'text': u'Post text'},
            {'title': u'Second post', 'abstract': u'<p>second post first line</p>',
             'description': u'Second post description', 'keywords': u'keyword3, keyword4',
             'text': u'Second post text'}
        ]
    }

    def setUp(self):
        super(ModelsTest, self).setUp()
        self.category_1 = BlogCategory.objects.create()
        self.category_1.name = u'category 1'
        self.category_1.save()
        self.thumb_1 = ThumbnailOption.objects.create(
            name='base', width=100, height=100, crop=True, upscale=False
        )
        self.thumb_2 = ThumbnailOption.objects.create(
            name='main', width=200, height=200, crop=False, upscale=False
        )

    def _get_post(self, data, post=None, lang='en'):
        if not post:
            post = Post()
        post.set_current_language(lang)
        post.author = self.user
        post.title = data['title']
        post.abstract = data['abstract']
        post.meta_description = data['description']
        post.meta_keywords = data['keywords']
        post.save()
        post.categories.add(self.category_1)
        post.save()
        return post

    def test_model_attributes(self):
        post = self._get_post(self.data['en'][0])
        post = self._get_post(self.data['it'][0], post, 'it')
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

        post.set_current_language('en')
        kwargs = {'year': post.date_published.year,
                  'month': post.date_published.month,
                  'day': post.date_published.day,
                  'slug': post.safe_translation_getter('slug', any_language=True)}
        url_en = reverse('djangocms_blog:post-detail', kwargs=kwargs)
        self.assertEqual(url_en, post.get_absolute_url())
        post.set_current_language('it')
        kwargs = {'year': post.date_published.year,
                  'month': post.date_published.month,
                  'day': post.date_published.day,
                  'slug': post.safe_translation_getter('slug', any_language=True)}
        url_it = reverse('djangocms_blog:post-detail', kwargs=kwargs)
        self.assertEqual(url_it, post.get_absolute_url())
        self.assertNotEqual(url_it, url_en)

        self.assertEqual(post.get_full_url(), 'http://example.com%s' % url_it)

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

    def test_manager(self):
        post_1 = self._get_post(self.data['en'][0])
        post_2 = self._get_post(self.data['en'][1])

        # default queryset, published and unpublished posts
        months = Post.objects.get_months()
        for data in months:
            self.assertEqual(data['date'], date(year=date.today().year, month=date.today().month, day=1))
            self.assertEqual(data['count'], 2)

        # custom queryset, only published
        post_1.publish = True
        post_1.save()
        months = Post.objects.get_months(Post.objects.published())
        for data in months:
            self.assertEqual(data['date'], date(year=date.today().year, month=date.today().month, day=1))
            self.assertEqual(data['count'], 1)

        self.assertEqual(len(Post.objects.available()), 1)

        # If post is published but publishing date is in the future
        post_2.date_published = date(year=date.today().year+1, month=date.today().month, day=1)
        post_2.publish = True
        post_2.save()
        self.assertEqual(len(Post.objects.available()), 2)
        self.assertEqual(len(Post.objects.published()), 1)
        self.assertEqual(len(Post.objects.archived()), 0)

        # If post is published but end publishing date is in the past
        post_2.date_published = date(year=date.today().year-2, month=date.today().month, day=1)
        post_2.date_published_end = date(year=date.today().year-1, month=date.today().month, day=1)
        post_2.save()
        self.assertEqual(len(Post.objects.available()), 2)
        self.assertEqual(len(Post.objects.published()), 1)
        self.assertEqual(len(Post.objects.archived()), 1)

        # counting with language fallback enabled
        post = self._get_post(self.data['it'][0], post_1, 'it')
        self.assertEqual(len(Post.objects.filter_by_language('it')), 2)

        # No fallback
        parler.appsettings.PARLER_LANGUAGES['default']['hide_untranslated'] = True
        self.assertEqual(len(Post.objects.filter_by_language('it')), 1)
        parler.appsettings.PARLER_LANGUAGES['default']['hide_untranslated'] = False

    def test_tag_cloud(self):
        post_1 = self._get_post(self.data['en'][0])
        post_2 = self._get_post(self.data['en'][1])
        post_1.tags.add('tag 1', 'tag 2', 'tag 3', 'tag 4')
        post_1.save()
        post_2.tags.add('tag 6', 'tag 2', 'tag 5', 'tag 8')
        post_2.save()

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

        post_1.publish = True
        post_1.save()
        self.assertEqual(set(Post.objects.tag_cloud()), set(tags_1))
        self.assertEqual(set(Post.objects.tag_cloud(published=False)), set(tags))

    def test_plugin_latest(self):
        post_1 = self._get_post(self.data['en'][0])
        post_2 = self._get_post(self.data['en'][1])
        post_1.tags.add('tag 1')
        post_1.save()
        plugin = add_plugin(post_1.content, 'BlogLatestEntriesPlugin', language='en')
        tag = Tag.objects.get(slug='tag-1')
        plugin.tags.add(tag)
        self.assertEqual(len(plugin.get_posts()), 0)
        post_1.publish = True
        post_1.save()
        self.assertEqual(len(plugin.get_posts()), 1)

    def test_copy_plugin_latest(self):
        post_1 = self._get_post(self.data['en'][0])
        post_2 = self._get_post(self.data['en'][1])
        tag = Tag.objects.create(name='tag 1')
        plugin = add_plugin(post_1.content, 'BlogLatestEntriesPlugin', language='en')
        plugin.tags.add(tag)
        plugins = list(post_1.content.cmsplugin_set.filter(language='en').order_by('tree_id', 'level', 'position'))
        copy_plugins_to(plugins, post_2.content)
        new = downcast_plugins(post_2.content.cmsplugin_set.all())
        self.assertEqual(set(new[0].tags.all()), set([tag]))

    def test_plugin_author(self):
        post_1 = self._get_post(self.data['en'][0])
        post_2 = self._get_post(self.data['en'][1])
        plugin = add_plugin(post_1.content, 'BlogAuthorPostsPlugin', language='en')
        plugin.authors.add(self.user)
        self.assertEqual(len(plugin.get_posts()), 0)
        self.assertEqual(plugin.get_authors()[0].count, 0)

        post_1.publish = True
        post_1.save()
        self.assertEqual(len(plugin.get_posts()), 1)
        self.assertEqual(plugin.get_authors()[0].count, 1)

        post_2.publish = True
        post_2.save()
        self.assertEqual(len(plugin.get_posts()), 2)
        self.assertEqual(plugin.get_authors()[0].count, 2)

    def test_copy_plugin_author(self):
        post_1 = self._get_post(self.data['en'][0])
        post_2 = self._get_post(self.data['en'][1])
        plugin = add_plugin(post_1.content, 'BlogAuthorPostsPlugin', language='en')
        plugin.authors.add(self.user)
        plugins = list(post_1.content.cmsplugin_set.filter(language='en').order_by('tree_id', 'level', 'position'))
        copy_plugins_to(plugins, post_2.content)
        new = downcast_plugins(post_2.content.cmsplugin_set.all())
        self.assertEqual(set(new[0].authors.all()), set([self.user]))

        """
                'title': 'title',
        'description': 'get_description',
        'og_description': 'get_description',
        'twitter_description': 'get_description',
        'gplus_description': 'get_description',
        'keywords': 'get_keywords',
        'locale': None,
        'image': 'get_image_url',
        'object_type': settings.BLOG_TYPE,
        'og_type': settings.BLOG_FB_TYPE,
        'og_app_id': settings.BLOG_FB_APPID,
        'og_profile_id': settings.BLOG_FB_PROFILE_ID,
        'og_publisher': settings.BLOG_FB_PUBLISHER,
        'og_author_url': settings.BLOG_FB_AUTHOR_URL,
        'twitter_type': settings.BLOG_TWITTER_TYPE,
        'twitter_site': settings.BLOG_TWITTER_SITE,
        'twitter_author': settings.BLOG_TWITTER_AUTHOR,
        'gplus_type': settings.BLOG_GPLUS_TYPE,
        'gplus_author': settings.BLOG_GPLUS_AUTHOR,
        'published_time': 'date_published',
        'modified_time': 'date_modified',
        'expiration_time': 'date_published_end',
        'tag': 'get_tags',
        'url': 'get_absolute_url',"""