# -*- coding: utf-8 -*-
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _



@toolbar_pool.register
class BlogToolbar(CMSToolbar):

    def populate(self):
        admin_menu = self.toolbar.get_or_create_menu("djangocms_blog", _('Blog'))
        url = reverse('admin:djangocms_blog_post_changelist')
        admin_menu.add_modal_item(_('Post list'), url=url)
        url = reverse('admin:djangocms_blog_post_add')
        admin_menu.add_modal_item(_('Add post'), url=url)