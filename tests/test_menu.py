# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from aldryn_apphooks_config.utils import get_app_instance
from django.utils.translation import activate
from menus.menu_pool import menu_pool
from parler.utils.context import smart_override, switch_language

from djangocms_blog.models import BlogCategory
from djangocms_blog.settings import (
    MENU_TYPE_CATEGORIES, MENU_TYPE_COMPLETE, MENU_TYPE_NONE, MENU_TYPE_POSTS,
)
from djangocms_blog.views import CategoryEntriesView, PostDetailView

from .base import BaseTest


class MenuTest(BaseTest):
    cats = []

    def setUp(self):
        super(MenuTest, self).setUp()
        self.cats = [self.category_1]
        for i, lang_data in enumerate(self._categories_data):
            cat = self._get_category(lang_data['en'])
            if 'it' in lang_data:
                cat = self._get_category(lang_data['it'], cat, 'it')
            self.cats.append(cat)

        activate('en')
        self._reload_menus()

    def test_menu_nodes(self):
        """
        Tests if all categories are present in the menu
        """
        pages = self.get_pages()
        posts = self.get_posts()
        self.reload_urlconf()

        for lang in ('en', 'it'):
            with smart_override(lang):
                self._reset_menus()
                request = self.get_page_request(pages[1], self.user, pages[1].get_absolute_url(lang), edit=True)
                nodes = self.get_nodes(menu_pool, request)
                self.assertTrue(len(nodes), BlogCategory.objects.all().count() + len(pages))
                nodes_url = set([node.get_absolute_url() for node in nodes])
                cats_url = set([cat.get_absolute_url() for cat in self.cats if cat.has_translation(lang)])
                self.assertTrue(cats_url.issubset(nodes_url))

        self._reset_menus()
        posts[0].categories.clear()
        for lang in ('en', 'it'):
            with smart_override(lang):
                self._reset_menus()
                request = self.get_page_request(pages[1].get_draft_object(), self.user, pages[1].get_draft_object().get_absolute_url(lang))
                nodes = self.get_nodes(menu_pool, request)
                urls = [node.get_absolute_url() for node in nodes]
                nodes_url = [node.get_absolute_url() for node in nodes]
                self.assertTrue(len(nodes_url), BlogCategory.objects.all().count() + len(pages))
                self.assertFalse(posts[0].get_absolute_url(lang) in nodes_url)
                self.assertTrue(posts[1].get_absolute_url(lang) in nodes_url)

    def test_menu_options(self):
        """
        Tests menu structure based on menu_structure configuration
        """
        self.get_pages()
        posts = self.get_posts()

        cats_url = {}
        cats_with_post_url = {}
        cats_without_post_url = {}
        posts_url = {}

        languages = ('en', 'it')

        for lang in languages:
            with smart_override(lang):
                self._reset_menus()
                cats_url[lang] = set([cat.get_absolute_url() for cat in self.cats if cat.has_translation(lang)])
                cats_with_post_url[lang] = set([cat.get_absolute_url() for cat in self.cats if cat.has_translation(lang) and cat.blog_posts.published().exists()])
                cats_without_post_url[lang] = cats_url[lang].difference(cats_with_post_url[lang])
                posts_url[lang] = set([post.get_absolute_url(lang) for post in posts if post.has_translation(lang) and post.app_config == self.app_config_1])

        # No item in the menu
        self.app_config_1.app_data.config.menu_structure = MENU_TYPE_NONE
        self.app_config_1.save()
        self._reset_menus()
        for lang in languages:
            request = self.get_page_request(None, self.user, r'/%s/page-two/' % lang)
            with smart_override(lang):
                self._reset_menus()
                nodes = self.get_nodes(menu_pool, request)
                nodes_url = set([node.get_absolute_url() for node in nodes])
                self.assertFalse(cats_url[lang].issubset(nodes_url))
                self.assertFalse(posts_url[lang].issubset(nodes_url))

        # Only posts in the menu
        self.app_config_1.app_data.config.menu_structure = MENU_TYPE_POSTS
        self.app_config_1.save()
        self._reset_menus()
        for lang in languages:
            request = self.get_page_request(None, self.user, r'/%s/page-two/' % lang)
            with smart_override(lang):
                self._reset_menus()
                nodes = self.get_nodes(menu_pool, request)
                nodes_url = set([node.get_absolute_url() for node in nodes])
                self.assertFalse(cats_url[lang].issubset(nodes_url))
                self.assertTrue(posts_url[lang].issubset(nodes_url))

        # Only categories in the menu
        self.app_config_1.app_data.config.menu_structure = MENU_TYPE_CATEGORIES
        self.app_config_1.save()
        self._reset_menus()
        for lang in languages:
            request = self.get_page_request(None, self.user, r'/%s/page-two/' % lang)
            with smart_override(lang):
                self._reset_menus()
                nodes = self.get_nodes(menu_pool, request)
                nodes_url = set([node.get_absolute_url() for node in nodes])
                self.assertTrue(cats_url[lang].issubset(nodes_url))
                self.assertFalse(posts_url[lang].issubset(nodes_url))

        # Both types in the menu
        self.app_config_1.app_data.config.menu_structure = MENU_TYPE_COMPLETE
        self.app_config_1.save()
        self._reset_menus()
        for lang in languages:
            request = self.get_page_request(None, self.user, r'/%s/page-two/' % lang)
            with smart_override(lang):
                self._reset_menus()
                nodes = self.get_nodes(menu_pool, request)
                nodes_url = set([node.get_absolute_url() for node in nodes])
                self.assertTrue(cats_url[lang].issubset(nodes_url))
                self.assertTrue(posts_url[lang].issubset(nodes_url))

        # Both types in the menu
        self.app_config_1.app_data.config.menu_empty_categories = False
        self.app_config_1.save()
        self.app_config_2.app_data.config.menu_empty_categories = False
        self.app_config_2.save()
        self._reset_menus()
        for lang in languages:
            request = self.get_page_request(None, self.user, r'/%s/page-two/' % lang)
            with smart_override(lang):
                self._reset_menus()
                nodes = self.get_nodes(menu_pool, request)
                nodes_url = set([node.url for node in nodes])
                self.assertTrue(cats_with_post_url[lang].issubset(nodes_url))
                self.assertFalse(cats_without_post_url[lang].intersection(nodes_url))
                self.assertTrue(posts_url[lang].issubset(nodes_url))
        # Both types in the menu
        self.app_config_1.app_data.config.menu_empty_categories = True
        self.app_config_1.save()
        self.app_config_2.app_data.config.menu_empty_categories = True
        self.app_config_2.save()
        self._reset_menus()

    def test_modifier(self):
        """
        Tests if correct category is selected in the menu
        according to context (view object)
        """
        pages = self.get_pages()
        posts = self.get_posts()

        tests = (
            # view class, view kwarg, view object, category
            (PostDetailView, 'slug', posts[0], posts[0].categories.first()),
            (CategoryEntriesView, 'category', self.cats[2], self.cats[2])
        )
        self.app_config_1.app_data.config.menu_structure = MENU_TYPE_COMPLETE
        self.app_config_1.save()
        for view_cls, kwarg, obj, cat in tests:
            with smart_override('en'):
                with switch_language(obj, 'en'):
                    request = self.get_page_request(
                        pages[1], self.user, path=obj.get_absolute_url()
                    )
                    self._reset_menus()
                    menu_pool.clear(all=True)
                    view_obj = view_cls()
                    view_obj.request = request
                    view_obj.namespace, view_obj.config = get_app_instance(request)
                    view_obj.app_config = self.app_config_1
                    view_obj.kwargs = {kwarg: obj.slug}
                    view_obj.get(request)
                    view_obj.get_context_data()
                    # check if selected menu node points to cat
                    nodes = self.get_nodes(menu_pool, request)
                    found = []
                    for node in nodes:
                        if node.selected:
                            found.append(node.get_absolute_url())
                    self.assertTrue(obj.get_absolute_url() in found)

        self.app_config_1.app_data.config.menu_structure = MENU_TYPE_CATEGORIES
        self.app_config_1.save()
        for view_cls, kwarg, obj, cat in tests:
            with smart_override('en'):
                with switch_language(obj, 'en'):
                    request = self.get_page_request(
                        pages[1], self.user, path=obj.get_absolute_url()
                    )
                    self._reset_menus()
                    menu_pool.clear(all=True)
                    view_obj = view_cls()
                    view_obj.request = request
                    view_obj.namespace, view_obj.config = get_app_instance(request)
                    view_obj.app_config = self.app_config_1
                    view_obj.kwargs = {kwarg: obj.slug}
                    view_obj.get(request)
                    view_obj.get_context_data()
                    # check if selected menu node points to cat
                    nodes = self.get_nodes(menu_pool, request)
                    found = [node.get_absolute_url() for node in nodes if node.selected]
                    self.assertTrue(cat.get_absolute_url() in found)

        self.app_config_1.app_data.config.menu_structure = MENU_TYPE_COMPLETE
        self.app_config_1.save()
