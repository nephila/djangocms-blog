# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from django.core.urlresolvers import reverse
from django.utils.translation import override, ugettext_lazy as _

from .models import BLOG_CURRENT_NAMESPACE, BLOG_CURRENT_POST_IDENTIFIER


@toolbar_pool.register
class BlogToolbar(CMSToolbar):

    def populate(self):
        # TODO: Readd if not self.is_current_app condition when CMS 3.0.4 is released
        if not self.request.user.has_perm('djangocms_blog.add_post'):
            return   # pragma: no cover
        admin_menu = self.toolbar.get_or_create_menu('djangocms_blog', _('Blog'))
        with override(self.current_lang):
            url = reverse('admin:djangocms_blog_post_changelist')
            admin_menu.add_modal_item(_('Post list'), url=url)
            url = reverse('admin:djangocms_blog_post_add')
            admin_menu.add_modal_item(_('Add post'), url=url)
            current_config = getattr(self.request, BLOG_CURRENT_NAMESPACE, None)
            if current_config:
                url = reverse('admin:djangocms_blog_blogconfig_change', args=(current_config.pk,))
                admin_menu.add_modal_item(_('Edit configuration'), url=url)

            current_post = getattr(self.request, BLOG_CURRENT_POST_IDENTIFIER, None)
            if current_post and self.request.user.has_perm('djangocms_blog.change_post'):  # pragma: no cover  # NOQA
                admin_menu.add_modal_item(_('Edit Post'), reverse(
                    'admin:djangocms_blog_post_change', args=(current_post.pk,)),
                    active=True)

    def post_template_populate(self):
        current_post = getattr(self.request, BLOG_CURRENT_POST_IDENTIFIER, None)
        if current_post and self.request.user.has_perm('djangocms_blog.change_post'):  # pragma: no cover  # NOQA
            # removing page meta menu, if present, to avoid confusion
            try:   # pragma: no cover
                import djangocms_page_meta  # NOQA
                menu = self.request.toolbar.get_or_create_menu('page')
                pagemeta = menu.get_or_create_menu('pagemeta', 'meta')
                menu.remove_item(pagemeta)
            except ImportError:
                pass
            # removing page tags menu, if present, to avoid confusion
            try:   # pragma: no cover
                import djangocms_page_tags  # NOQA
                menu = self.request.toolbar.get_or_create_menu('page')
                pagetags = menu.get_or_create_menu('pagetags', 'tags')
                menu.remove_item(pagetags)
            except ImportError:
                pass
