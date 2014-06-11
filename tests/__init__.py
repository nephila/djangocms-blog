# -*- coding: utf-8 -*-
"""
Tests for `djangocms_blog` module.
"""
from cms.utils.i18n import get_language_list
from cmsplugin_filer_image.models import ThumbnailOption
from django.contrib.auth.models import User
from django.http import SimpleCookie
from django.test import TestCase, RequestFactory
from django.utils.translation import activate
from six import StringIO

from djangocms_blog.models import BlogCategory, Post


class BaseTest(TestCase):
    """
    Base class with utility function
    """
    request_factory = None
    user = None
    languages = get_language_list()
    category_1 = None
    thumb_1 = None
    thumb_2 = None

    data = {
        'it': [
            {'title': u'Primo post', 'abstract': u'<p>prima riga</p>',
             'description': u'Questa è la descrizione', 'keywords': u'keyword1, keyword2',
             'text': u'Testo del post',},
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

    @classmethod
    def setUpClass(cls):
        cls.request_factory = RequestFactory()
        cls.user = User.objects.create(username='admin', is_staff=True, is_superuser=True)
        cls.user_staff = User.objects.create(username='staff', is_staff=True)
        cls.user_normal = User.objects.create(username='normal')

    def setUp(self):
        activate('en')
        super(BaseTest, self).setUp()
        self.category_1 = BlogCategory.objects.create()
        self.category_1.name = u'category 1'
        self.category_1.save()
        self.category_1.set_current_language('it')
        self.category_1.name = u'categoria 1'
        self.category_1.save()
        self.category_1.set_current_language('en')
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

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()

    def get_pages(self):
        from cms.api import create_page, create_title
        page = create_page(u'page one', 'page.html', language='en')
        page_2 = create_page(u'page two', 'page.html', language='en')
        create_title(language='fr', title=u'page un', page=page)
        create_title(language='it', title=u'pagina uno', page=page)
        for lang in self.languages:
            page.publish(lang)
        page_2.publish('en')
        return page.get_draft_object(), page_2.get_draft_object()

    def get_request(self, page, lang):
        request = self.request_factory.get(page.get_path(lang))
        request.current_page = page
        request.user = self.user
        request.session = {}
        request.cookies = SimpleCookie()
        request.errors = StringIO()
        return request

    def get_page_request(self, page, user, path=None, edit=False, lang_code='en'):
        from cms.middleware.toolbar import ToolbarMiddleware
        path = path or page and page.get_absolute_url()
        if edit:
            path += '?edit'
        request = RequestFactory().get(path)
        request.session = {}
        request.user = user
        request.LANGUAGE_CODE = lang_code
        if edit:
            request.GET = {'edit': None}
        else:
            request.GET = {'edit_off': None}
        request.current_page = page
        mid = ToolbarMiddleware()
        mid.process_request(request)
        return request

    def get_posts(self):
        post1 = self._get_post(self.data['en'][0])
        post1 = self._get_post(self.data['it'][0], post1, 'it')
        post1.publish = True
        post1.save()
        post1.set_current_language('en')
        post2 = self._get_post(self.data['en'][1])
        post2 = self._get_post(self.data['it'][1], post2, 'it')
        post2.set_current_language('en')
        return post1, post2