# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.menu_bases import CMSAttachMenu
from django.db.models.signals import post_delete, post_save
from django.utils.translation import get_language_from_request, ugettext_lazy as _
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from .cms_appconfig import BlogConfig
from .models import BlogCategory, Post
from .settings import MENU_TYPE_CATEGORIES, MENU_TYPE_COMPLETE, MENU_TYPE_POSTS


class BlogCategoryMenu(CMSAttachMenu):
    name = _('Blog menu')

    def get_nodes(self, request):
        nodes = []

        language = get_language_from_request(request, check_path=True)

        categories_menu = False
        posts_menu = False
        config = False
        if hasattr(self, 'instance') and self.instance:
            config = BlogConfig.objects.get(namespace=self.instance.application_namespace)
        if config.menu_structure in (MENU_TYPE_COMPLETE, MENU_TYPE_CATEGORIES):
            categories_menu = True
        if config.menu_structure in (MENU_TYPE_COMPLETE, MENU_TYPE_POSTS):
            posts_menu = True

        if categories_menu:
            categories = BlogCategory.objects
            if config:
                categories = categories.namespace(self.instance.application_namespace)
            categories = categories.active_translations(language).distinct()
            categories = categories.order_by('parent__id', 'translations__name')
            for category in categories:
                node = NavigationNode(
                    category.name,
                    category.get_absolute_url(),
                    '%s-%s' % (category.__class__.__name__, category.pk),
                    ('%s-%s' % (category.__class__.__name__, category.parent.id) if category.parent
                     else None)
                )
                nodes.append(node)

        if posts_menu:
            posts = Post.objects
            if hasattr(self, 'instance') and self.instance:
                posts = posts.namespace(self.instance.application_namespace)
            posts = posts.active_translations(language).distinct()
            for post in posts:
                if categories_menu:
                    category = post.categories.first()
                    parent = '%s-%s' % (category.__class__.__name__, category.pk)
                    post_id = '%s-%s' % (post.__class__.__name__, post.pk),
                else:
                    parent = None
                    post_id = '%s-%s' % (post.__class__.__name__, post.pk),
                node = NavigationNode(
                    post.get_title(),
                    post.get_absolute_url(language),
                    post_id,
                    parent
                )
                nodes.append(node)

        return nodes

menu_pool.register_menu(BlogCategoryMenu)


def clear_menu_cache(**kwargs):
    menu_pool.clear(all=True)

post_save.connect(clear_menu_cache, sender=BlogCategory)
post_delete.connect(clear_menu_cache, sender=BlogCategory)
