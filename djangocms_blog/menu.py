# -*- coding: utf-8 -*-
from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _, get_language
from .models import BlogCategory


class BlogCategoryMenu(CMSAttachMenu):
    name = _('Blog Category menu')

    def get_nodes(self, request):
        nodes = []
        qs = BlogCategory.objects.translated(get_language())
        qs = qs.order_by('parent_id', 'translations__name')
        for category in qs:
            kwargs = { 'category': category.slug }
            node = NavigationNode(
                category.name,
                category.get_absolute_url(),
                category.pk,
                category.parent_id
            )
            nodes.append(node)
        return nodes

menu_pool.register_menu(BlogCategoryMenu)

