# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.apphook_pool import apphook_pool
from cms.menu_bases import CMSAttachMenu
from django.core.urlresolvers import resolve
from django.db.models.signals import post_delete, post_save
from django.utils.translation import get_language_from_request, ugettext_lazy as _
from menus.base import Modifier, NavigationNode
from menus.menu_pool import menu_pool

from .cms_appconfig import BlogConfig
from .models import BlogCategory, Post
from .settings import MENU_TYPE_CATEGORIES, MENU_TYPE_COMPLETE, MENU_TYPE_POSTS, get_setting

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    from django.contrib.sites.models import get_current_site


class BlogCategoryMenu(CMSAttachMenu):
    """
    Main menu class

    Handles all types of blog menu
    """
    name = _('Blog menu')
    _config = {}

    def get_nodes(self, request):
        """
        Generates the nodelist

        :param request:
        :return: list of nodes
        """
        nodes = []

        language = get_language_from_request(request, check_path=True)
        current_site = get_current_site(request)

        if self.instance.site != current_site:
            return []

        categories_menu = False
        posts_menu = False
        config = False
        if hasattr(self, 'instance') and self.instance:
            if not self._config.get(self.instance.application_namespace, False):
                self._config[self.instance.application_namespace] = BlogConfig.objects.get(
                    namespace=self.instance.application_namespace
                )
            config = self._config[self.instance.application_namespace]
        if hasattr(self, 'instance') and self.instance:
            if not getattr(request, 'toolbar', False) or not request.toolbar.edit_mode:
                if self.instance == self.instance.get_draft_object():
                    return []
            else:
                if self.instance == self.instance.get_public_object():
                    return []
        if config and config.menu_structure in (MENU_TYPE_COMPLETE, MENU_TYPE_CATEGORIES):
            categories_menu = True
        if config and config.menu_structure in (MENU_TYPE_COMPLETE, MENU_TYPE_POSTS):
            posts_menu = True

        if categories_menu:
            categories = BlogCategory.objects
            if config:
                categories = categories.namespace(self.instance.application_namespace)
            categories = categories.active_translations(language)
            categories = categories.order_by('parent__id', 'translations__name').\
                select_related('app_config').prefetch_related('translations')
            added_categories = []
            for category in categories:
                if category.pk not in added_categories:
                    node = NavigationNode(
                        category.name,
                        category.get_absolute_url(),
                        '{0}-{1}'.format(category.__class__.__name__, category.pk),
                        (
                            '{0}-{1}'.format(
                                category.__class__.__name__, category.parent_id
                            ) if category.parent_id else None
                        )
                    )
                    nodes.append(node)
                    added_categories.append(category.pk)

        if posts_menu:
            posts = Post.objects
            if hasattr(self, 'instance') and self.instance:
                posts = posts.namespace(self.instance.application_namespace)
            posts = posts.active_translations(language).distinct().\
                select_related('app_config').prefetch_related('translations', 'categories')
            for post in posts:
                post_id = None
                parent = None
                if categories_menu:
                    category = post.categories.first()
                    if category:
                        parent = '{0}-{1}'.format(category.__class__.__name__, category.pk)
                        post_id = '{0}-{1}'.format(post.__class__.__name__, post.pk),
                else:
                    post_id = '{0}-{1}'.format(post.__class__.__name__, post.pk),
                if post_id:
                    node = NavigationNode(
                        post.get_title(),
                        post.get_absolute_url(language),
                        post_id,
                        parent
                    )
                    nodes.append(node)

        return nodes


class BlogNavModifier(Modifier):
    """
    This navigation modifier makes sure that when
    a particular blog post is viewed,
    a corresponding category is selected in menu
    """
    _config = {}

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        """
        Actual modifier function
        :param request: request
        :param nodes: complete list of nodes
        :param namespace: Menu namespace
        :param root_id: eventual root_id
        :param post_cut: flag for modifier stage
        :param breadcrumb: flag for modifier stage
        :return: nodeslist
        """
        app = None
        config = None
        if getattr(request, 'current_page', None) and request.current_page.application_urls:
            app = apphook_pool.get_apphook(request.current_page.application_urls)

        if app and app.app_config:
            namespace = resolve(request.path).namespace
            if not self._config.get(namespace, False):
                self._config[namespace] = app.get_config(namespace)
            config = self._config[namespace]
        try:
            if config and (
                    not isinstance(config, BlogConfig) or
                    config.menu_structure != MENU_TYPE_CATEGORIES
            ):
                return nodes
        except AttributeError:  # pragma: no cover
            # in case `menu_structure` is not present in config
            return nodes
        if post_cut:
            return nodes
        current_post = getattr(request, get_setting('CURRENT_POST_IDENTIFIER'), None)
        category = None
        if current_post and current_post.__class__ == Post:
            category = current_post.categories.first()
        if not category:
            return nodes

        for node in nodes:
            if '{0}-{1}'.format(category.__class__.__name__, category.pk) == node.id:
                node.selected = True
        return nodes


menu_pool.register_modifier(BlogNavModifier)
menu_pool.register_menu(BlogCategoryMenu)


def clear_menu_cache(**kwargs):
    """
    Empty menu cache when saving categories
    """
    menu_pool.clear(all=True)


post_save.connect(clear_menu_cache, sender=BlogCategory)
post_delete.connect(clear_menu_cache, sender=BlogCategory)
