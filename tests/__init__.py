# -*- coding: utf-8 -*-
"""
Tests for `djangocms_blog` module.
"""
from __future__ import absolute_import, print_function, unicode_literals

from cmsplugin_filer_image.models import ThumbnailOption
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils.translation import activate
from djangocms_helper.base_test import BaseTestCase

from djangocms_blog.models import BlogCategory, Post

User = get_user_model()


def _get_cat_pk(lang, name):
    return lambda: BlogCategory.objects.translated(lang, name=name).get().pk


class BaseTest(BaseTestCase):
    """
    Base class with utility function
    """
    category_1 = None
    thumb_1 = None
    thumb_2 = None

    _pages_data = (
        {'en': {'title': 'page one', 'template': 'page.html', 'publish': True},
         'fr': {'title': 'page un', 'publish': True},
         'it': {'title': 'pagina uno', 'publish': True}},
        {'en': {'title': 'page two', 'template': 'page.html', 'publish': True},
         'fr': {'title': 'page deux', 'publish': True},
         'it': {'title': 'pagina due', 'publish': True}},
    )

    data = {
        'it': [
            {'title': u'Primo post', 'abstract': u'<p>prima riga</p>',
             'description': u'Questa è la descrizione', 'keywords': u'keyword1, keyword2',
             'text': u'Testo del post'},
            {'title': u'Secondo post', 'abstract': u'<p>prima riga del secondo post</p>',
             'description': u'Descrizione del secondo post', 'keywords': u'keyword3, keyword4',
             'text': u'Testo del secondo post'},
            {'title': u'Terzo post', 'abstract': u'<p>prima riga del terzo post</p>',
             'description': u'Descrizione del terzo post', 'keywords': u'keyword5, keyword6',
             'text': u'Testo del terzo post'},
        ],
        'en': [
            {'title': u'First post', 'abstract': u'<p>first line</p>',
             'description': u'This is the description', 'keywords': u'keyword1, keyword2',
             'text': u'Post text'},
            {'title': u'Second post', 'abstract': u'<p>second post first line</p>',
             'description': u'Second post description', 'keywords': u'keyword3, keyword4',
             'text': u'Second post text'},
            {'title': u'Third post', 'abstract': u'<p>third post first line</p>',
             'description': u'third post description', 'keywords': u'keyword5, keyword6',
             'text': u'Third post text'}
        ]
    }

    cat_data = {
        'it': [
            {'name': u'Fortissimo'},
            {'name': u'Pianississimo'},
            {'name': u'Mezzo'},
            {'name': u'Forte', 'parent_id': _get_cat_pk('it', 'Mezzo')},
        ],
        'en': [
            {'name': u'Very loud'},
            {'name': u'Very very silent'},
            {'name': u'Almost'},
            {'name': u'Loud', 'parent_id': _get_cat_pk('en', 'Almost')},
            {'name': u'Silent', 'parent_id': _get_cat_pk('en', 'Almost')},
        ]
    }

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.site_2 = Site.objects.create(domain='http://example2.com', name='example 2')

    def setUp(self):
        activate('en')
        super(BaseTest, self).setUp()
        self.category_1 = BlogCategory.objects.create(name=u'category 1')
        self.category_1.set_current_language('it', initialize=True)
        self.category_1.name = u'categoria 1'
        self.category_1.save()
        self.thumb_1 = ThumbnailOption.objects.create(
            name='base', width=100, height=100, crop=True, upscale=False
        )
        self.thumb_2 = ThumbnailOption.objects.create(
            name='main', width=200, height=200, crop=False, upscale=False
        )
        self.img = self.create_filer_image_object()

    def tearDown(self):
        for post in Post.objects.all():
            post.delete()
        super(BaseTest, self).tearDown()

    def _get_category(self, data, category=None, lang='en'):
        for k, v in data.items():
            if hasattr(v, '__call__'):
                data[k] = v()
        if not category:
            category = BlogCategory.objects.create(**data)
        else:
            category.set_current_language(lang)
            for attr, val in data.items():
                setattr(category, attr, val)
            category.save()
        return category

    def _get_post(self, data, post=None, lang='en', sites=None):
        if not post:
            post_data = {
                'author': self.user,
                'title': data['title'],
                'abstract': data['abstract'],
                'meta_description': data['description'],
                'meta_keywords': data['keywords'],
            }
            post = Post.objects.create(**post_data)
        else:
            post.set_current_language(lang)
            post.title = data['title']
            post.abstract = data['abstract']
            post.meta_description = data['description']
            post.meta_keywords = data['keywords']
            post.save()
        post.categories.add(self.category_1)
        if sites:
            for site in sites:
                post.sites.add(site)
        return post

    def get_posts(self, sites=None):
        post1 = self._get_post(self.data['en'][0], sites=sites)
        post1 = self._get_post(self.data['it'][0], post1, 'it')
        post1.publish = True
        post1.main_image = self.img
        post1.save()
        post2 = self._get_post(self.data['en'][1], sites=sites)
        post2 = self._get_post(self.data['it'][1], post2, 'it')
        post2.main_image = self.img
        post2.save()
        return post1, post2
