# -*- coding: utf-8 -*-
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


from .models import BLOG_CURRENT_POST_IDENTIFIER


@toolbar_pool.register
class BlogToolbar(CMSToolbar):

    def populate(self):
        if not (self.is_current_app and self.request.user.has_perm('djangocms_blog.add_post')):
            return
        admin_menu = self.toolbar.get_or_create_menu("djangocms_blog", _('Blog'))
        url = reverse('admin:djangocms_blog_post_changelist')
        admin_menu.add_modal_item(_('Post list'), url=url)
        url = reverse('admin:djangocms_blog_post_add')
        admin_menu.add_modal_item(_('Add post'), url=url)

        current_post = getattr(self.request, BLOG_CURRENT_POST_IDENTIFIER, None)
        if current_post and self.request.user.has_perm('djangocms_blog.change_post'):
            admin_menu.add_modal_item(_('Edit Post'),reverse(
                'admin:djangocms_blog_post_change', args=(current_post.pk,)),
                                      active=True)