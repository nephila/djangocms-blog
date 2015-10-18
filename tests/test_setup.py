# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import sys

from cms.api import create_page, create_title
from cms.models import Page
from cms.utils import get_language_list
from django.utils.translation import override

from djangocms_blog.cms_appconfig import BlogConfig

from .base import BaseTest


class SetupTest(BaseTest):

    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()

    def test_setup_from_url(self):

        # Tests starts with no page and no config
        self.assertFalse(Page.objects.exists())
        self.assertFalse(BlogConfig.objects.exists())

        # importing urls triggers the auto setup
        from djangocms_blog import urls  # NOQA

        # Home and blog, published and draft
        self.assertEqual(Page.objects.count(), 4)
        self.assertEqual(BlogConfig.objects.count(), 1)

    def setUp(self):
        self.reload_urlconf()
        delete = [
            'djangocms_blog',
            'djangocms_blog.urls',
        ]
        for module in delete:
            del sys.modules[module]

    def test_setup_filled(self):

        # Tests starts with no page and no config
        self.assertFalse(Page.objects.exists())
        self.assertFalse(BlogConfig.objects.exists())

        langs = get_language_list()
        home = None
        for lang in langs:
            with override(lang):
                if not home:
                    home = create_page(
                        'a new home', language=lang,
                        template='blog.html', in_navigation=True, published=True
                    )
                else:
                    create_title(
                        language=lang, title='a new home', page=home
                    )
                    home.publish(lang)

        # importing urls triggers the auto setup
        from djangocms_blog import urls  # NOQA

        # Home and blog, published and draft
        self.assertEqual(Page.objects.count(), 4)
        self.assertEqual(BlogConfig.objects.count(), 1)

        home = Page.objects.get_home()
        for lang in langs:
            self.assertEqual(home.get_title(lang), 'a new home')
