# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.toolbar.items import ModalItem
from django.core.urlresolvers import reverse

from djangocms_blog.models import BLOG_CURRENT_POST_IDENTIFIER

from . import BaseTest


class ToolbarTest(BaseTest):

    def test_toolbar_with_items(self):
        """
        Test that Blog toolbar is present and contains all items
        """
        from cms.toolbar.toolbar import CMSToolbar
        posts = self.get_posts()
        pages = self.get_pages()
        request = self.get_page_request(pages[0], self.user, r'/en/blog/', edit=True)
        setattr(request, BLOG_CURRENT_POST_IDENTIFIER, posts[0])
        toolbar = CMSToolbar(request)
        toolbar.get_left_items()
        blog_menu = toolbar.menus['djangocms_blog']
        self.assertEqual(len(blog_menu.find_items(ModalItem, url=reverse('admin:djangocms_blog_post_changelist'))), 1)
        self.assertEqual(len(blog_menu.find_items(ModalItem, url=reverse('admin:djangocms_blog_post_add'))), 1)
        self.assertEqual(len(blog_menu.find_items(ModalItem, url=reverse('admin:djangocms_blog_post_change', args=(posts[0].pk,)))), 1)
