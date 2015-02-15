# -*- coding: utf-8 -*-
from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from django.db.models.signals import post_save, post_delete
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


def clear_menu_cache(**kwargs):
    menu_pool.clear(all=True)

post_save.connect(clear_menu_cache, sender=BlogCategory)
post_delete.connect(clear_menu_cache, sender=BlogCategory)
