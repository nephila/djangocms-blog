# -*- coding: utf-8 -*-
"""
Tests for `djangocms_blog` module.
"""
from __future__ import absolute_import, print_function, unicode_literals

from copy import deepcopy

from cmsplugin_filer_image.models import ThumbnailOption
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from djangocms_helper.base_test import BaseTestCase
from parler.utils.context import smart_override

from djangocms_blog.cms_appconfig import BlogConfig
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
        {'en': {'title': 'page two', 'template': 'page.html', 'publish': True,
                'apphook': 'BlogApp', 'apphook_namespace': 'sample_app'},
         'fr': {'title': 'page deux', 'publish': True},
         'it': {'title': 'pagina due', 'publish': True}},
        {'en': {'title': 'page three', 'template': 'page.html', 'publish': True,
                'apphook': 'BlogApp', 'apphook_namespace': 'sample_app2'},
         'fr': {'title': 'page trois', 'publish': True},
         'it': {'title': 'pagina tre', 'publish': True}},
    )

    _post_data = (
        {'en': {'title': 'First post', 'abstract': '<p>first line</p>',
                'description': 'This is the description', 'keywords': 'keyword1, keyword2',
                'text': 'Post text', 'app_config': 'sample_app', 'publish': True},
         'it': {'title': 'Primo post', 'abstract': '<p>prima riga</p>',
                'description': 'Questa è la descrizione', 'keywords': 'keyword1, keyword2',
                'text': 'Testo del post'},
         },
        {'en': {'title': 'Second post', 'abstract': '<p>second post first line</p>',
                'description': 'Second post description', 'keywords': 'keyword3, keyword4',
                'text': 'Second post text', 'app_config': 'sample_app', 'publish': False},
         'it': {'title': 'Secondo post', 'abstract': '<p>prima riga del secondo post</p>',
                'description': 'Descrizione del secondo post', 'keywords': 'keyword3, keyword4',
                'text': 'Testo del secondo post', 'app_config': 'sample_app'},
         },
        {'en': {'title': 'Third post', 'abstract': '<p>third post first line</p>',
                'description': 'third post description', 'keywords': 'keyword5, keyword6',
                'text': 'Third post text', 'app_config': 'sample_app', 'publish': False},
         'it': {'title': 'Terzo post', 'abstract': '<p>prima riga del terzo post</p>',
                'description': 'Descrizione del terzo post', 'keywords': 'keyword5, keyword6',
                'text': 'Testo del terzo post'},
         },
        {'en': {'title': 'Different appconfig', 'abstract': '<p>Different appconfig first line</p>',
                'description': 'Different appconfig description', 'keywords': 'keyword5, keyword6',
                'text': 'Different appconfig text', 'app_config': 'sample_app2', 'publish': True},
         'it': {'title': 'Altro appconfig', 'abstract': '<p>prima riga del Altro appconfig</p>',
                'description': 'Descrizione Altro appconfig', 'keywords': 'keyword5, keyword6',
                'text': 'Testo del Altro appconfig'},
         },
    )

    _categories_data = (
        {'en': {'name': 'Very loud', 'app_config': 'sample_app'},
         'it': {'name': 'Fortissimo'},
         },
        {'en': {'name': 'Very very silent', 'app_config': 'sample_app'},
         'it': {'name': 'Pianississimo'},
         },
        {'en': {'name': 'Almost', 'app_config': 'sample_app'},
         'it': {'name': 'Mezzo'},
         },
        {'en': {'name': 'Loud', 'parent_id': _get_cat_pk('en', 'Almost'), 'app_config': 'sample_app'},
         'it': {'name': 'Forte', 'parent_id': _get_cat_pk('it', 'Mezzo')},
         },
        {'en': {'name': 'Silent', 'parent_id': _get_cat_pk('en', 'Almost'), 'app_config': 'sample_app'},
         },
        {'en': {'name': 'Drums', 'app_config': 'sample_app2'},
         'it': {'name': 'Tamburi'},
         },
        {'en': {'name': 'Guitars', 'app_config': 'sample_app2'},
         'it': {'name': 'Chitarre'},
         },
    )

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.thumb_1 = ThumbnailOption.objects.create(
            name='base', width=100, height=100, crop=True, upscale=False
        )
        cls.thumb_2 = ThumbnailOption.objects.create(
            name='main', width=200, height=200, crop=False, upscale=False
        )
        cls.app_config_1 = BlogConfig.objects.create(
            namespace='sample_app', app_title='app1'
        )
        cls.app_config_2 = BlogConfig.objects.create(
            namespace='sample_app2', app_title='app2'
        )
        cls.app_config_1.app_data.config.paginate_by = 1
        cls.app_config_1.save()
        cls.app_config_2.app_data.config.paginate_by = 2
        cls.app_config_2.save()
        cls.app_configs = {
            'sample_app': cls.app_config_1,
            'sample_app2': cls.app_config_2,
        }
        cls.category_1 = BlogCategory.objects.create(name='category 1', app_config=cls.app_config_1)
        cls.category_1.set_current_language('it', initialize=True)
        cls.category_1.name = 'categoria 1'
        cls.category_1.save()
        cls.site_2 = Site.objects.create(domain='http://example2.com', name='example 2')

    @classmethod
    def tearDownClass(cls):
        super(BaseTest, cls).tearDownClass()
        BlogConfig.objects.all().delete()
        BlogCategory.objects.all().delete()
        ThumbnailOption.objects.all().delete()

    def _get_category(self, data, category=None, lang='en'):
        data = deepcopy(data)
        for k, v in data.items():
            if hasattr(v, '__call__'):
                data[k] = v()
        if not category:
            with smart_override(lang):
                data['app_config'] = self.app_configs[data['app_config']]
                category = BlogCategory.objects.create(**data)
        else:
            category.set_current_language(lang, initialize=True)
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
                'app_config': self.app_configs[data['app_config']]
            }
            post = Post.objects.create(**post_data)
        else:
            post.create_translation(
                lang,
                title=data['title'],
                abstract=data['abstract'],
                meta_description=data['description'],
                meta_keywords=data['keywords']
            )
        post = self.reload_model(post)
        post.categories.add(self.category_1)
        if sites:
            for site in sites:
                post.sites.add(site)
        return post

    def get_posts(self, sites=None):
        posts = []
        for post in self._post_data:
            post1 = self._get_post(post['en'], sites=sites)
            post1 = self._get_post(post['it'], post=post1, lang='it')
            post1.publish = post['en']['publish']
            post1.main_image = self.create_filer_image_object()
            post1.save()
            posts.append(post1)
        return posts
