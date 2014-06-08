# -*- coding: utf-8 -*-
from cmsplugin_filer_image.models import ThumbnailOption
from django.core.urlresolvers import reverse
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