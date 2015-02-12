# -*- coding: utf-8 -*-
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, get_language
from .models import BlogCategory


class BlogCategoryMenu(CMSAttachMenu):
    name = _('Blog Category menu')

    def get_nodes(self, request):
        nodes = []
        qs = BlogCategory.objects.translated(get_language())
        qs = qs.order_by('parent_id', 'translations__name').distinct()
        for category in qs:
            kwargs = { 'category': category.slug }
            node = NavigationNode(
                category.name,
                reverse('djangocms_blog:posts-category', kwargs=kwargs),
                category.pk,
                category.parent_id
            )
            nodes.append(node)
        return nodes

menu_pool.register_menu(BlogCategoryMenu)

class BlogApp(CMSApp):
    name = _('Blog')
    urls = ['djangocms_blog.urls']
    app_name = 'djangocms_blog'
    menus = [BlogCategoryMenu]

apphook_pool.register(BlogApp)
