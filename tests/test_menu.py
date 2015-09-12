# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import copy

from django.utils.translation import activate
from menus.menu_pool import menu_pool
from parler.utils.context import switch_language

from djangocms_blog.views import CategoryEntriesView, PostDetailView

from . import BaseTest


class MenuTest(BaseTest):
    def setUp(self):
        super(MenuTest, self).setUp()
        self.cats = [self.category_1]
        for i, cat_data in enumerate(self.cat_data['en']):
            cat = self._get_category(cat_data)
            if i < len(self.cat_data['it']):
                cat = self._get_category(self.cat_data['it'][i], cat, 'it')
            self.cats.append(cat)

        activate('en')
        menu_pool.discover_menus()
        # All cms menu modifiers should be removed from menu_pool.modifiers
        # so that they do not interfere with our menu nodes
        menu_pool.modifiers = [m for m in menu_pool.modifiers if m.__module__.startswith('djangocms_blog')]

    def test_menu_nodes(self):
        """
        Tests if all categories are present in the menu
        """
        for lang in ('en', 'it'):
            request = self.get_page_request(None, self.user,
                                            r'/%s/blog/' % lang, edit=False)
            activate(lang)
            nodes = menu_pool.get_nodes(request, namespace='BlogCategoryMenu')
            nodes_copy = copy.deepcopy(nodes)
            for cat in self.cats:
                if not cat.has_translation(lang):
                    continue
                with switch_language(cat, lang):
                    # find in node list
                    found = None
                    for node in nodes_copy:
                        if node.url == cat.get_absolute_url():
                            found = node
                            break
                    self.assertIsNotNone(found)
                    nodes_copy.remove(found)
                    self.assertEqual(node.id, cat.id)
                    self.assertEqual(node.title, cat.name)
            # check that all categories were found in menu
            self.assertEqual(len(nodes_copy), 0)

    def test_modifier(self):
        """
        Tests if correct category is selected in the menu
        according to context (view object)
        """
        post1, post2 = self.get_posts()
        tests = (
            # view class, view kwarg, view object, category
            (PostDetailView, 'slug', post1, post1.categories.first()),
            (CategoryEntriesView, 'category', self.cats[2], self.cats[2])
        )
        for view_cls, kwarg, obj, cat in tests:
            request = self.get_page_request(None, self.user, r'/en/blog/', edit=False)
            activate('en')
            with switch_language(obj, 'en'):
                view_obj = view_cls()
                view_obj.request = request
                view_obj.kwargs = {kwarg: obj.slug}
                view_obj.get(request)
                # check if selected menu node points to cat
                nodes = menu_pool.get_nodes(request, namespace='BlogCategoryMenu')
                found = False
                for node in nodes:
                    if node.selected:
                        self.assertEqual(node.url, cat.get_absolute_url())
                        found = True
                        break
                self.assertTrue(found)
