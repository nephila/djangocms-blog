# -*- coding: utf-8 -*-
from cms.menu_bases import CMSAttachMenu
from menus.base import Modifier, NavigationNode
from menus.menu_pool import menu_pool
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _, get_language
from .models import BlogCategory


class BlogCategoryMenu(CMSAttachMenu):
    name = _('Blog Category menu')

    def get_nodes(self, request):
        nodes = []
        qs = BlogCategory.objects.translated(get_language())
        qs = qs.order_by('parent__id', 'translations__name')
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


class BlogNavModifier(Modifier):
    """
    This navigation modifier makes sure that when 
    a particular blog post is viewed, 
    a corresponding category is selected in menu
    """
    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if not post_cut: return nodes
        if not hasattr(request, 'toolbar'):
            return nodes
        if request.toolbar.get_object_model() != 'djangocms_blog.post':
            return nodes
        cat = request.toolbar.obj.categories.first()
        if not cat: return nodes

        for node in nodes:
            if (node.namespace == BlogCategoryMenu.__name__ and
                    cat.pk == node.id):
                node.selected = True
                break
        return nodes

menu_pool.register_modifier(BlogNavModifier)

def clear_menu_cache(**kwargs):
    menu_pool.clear(all=True)

post_save.connect(clear_menu_cache, sender=BlogCategory)
post_delete.connect(clear_menu_cache, sender=BlogCategory)
