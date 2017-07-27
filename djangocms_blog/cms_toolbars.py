# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.cms_toolbars import LANGUAGE_MENU_IDENTIFIER, ADD_PAGE_LANGUAGE_BREAK
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.i18n import get_language_dict
from cms.utils.urlutils import admin_reverse
from django.core.urlresolvers import reverse
from django.utils.translation import override, ugettext_lazy as _

from .settings import get_setting


@toolbar_pool.register
class BlogToolbar(CMSToolbar):

    def populate(self):
        if (not self.is_current_app and not get_setting('ENABLE_THROUGH_TOOLBAR_MENU')) or \
                not self.request.user.has_perm('djangocms_blog.add_post'):
            return   # pragma: no cover
        admin_menu = self.toolbar.get_or_create_menu('djangocms_blog', _('Blog'))
        self.add_copy_language_to_menu()
        with override(self.current_lang):
            url = reverse('admin:djangocms_blog_post_changelist')
            admin_menu.add_modal_item(_('Post list'), url=url)
            url = reverse('admin:djangocms_blog_post_add')
            admin_menu.add_modal_item(_('Add post'), url=url)
            current_config = getattr(self.request, get_setting('CURRENT_NAMESPACE'), None)
            if current_config:
                url = reverse('admin:djangocms_blog_blogconfig_change', args=(current_config.pk,))
                admin_menu.add_modal_item(_('Edit configuration'), url=url)

            current_post = getattr(self.request, get_setting('CURRENT_POST_IDENTIFIER'), None)
            if current_post and self.request.user.has_perm('djangocms_blog.change_post'):  # pragma: no cover  # NOQA
                admin_menu.add_modal_item(_('Edit Post'), reverse(
                    'admin:djangocms_blog_post_change', args=(current_post.pk,)),
                    active=True)

    def add_publish_button(self):
        """
        Adds the publish button to the toolbar if the current post is unpublished
        """
        current_post = getattr(self.request, get_setting('CURRENT_POST_IDENTIFIER'), None)
        if (self.toolbar.edit_mode and current_post and
                not current_post.publish and
                self.request.user.has_perm('djangocms_blog.change_post')
            ):  # pragma: no cover  # NOQA
            classes = ['cms-btn-action', 'blog-publish']
            title = _('Publish {0} now').format(current_post.app_config.object_name)

            url = admin_reverse('djangocms_blog_publish_article', args=(current_post.pk,))

            self.toolbar.add_button(title, url=url, extra_classes=classes, side=self.toolbar.RIGHT)

    def post_template_populate(self):
        current_post = getattr(self.request, get_setting('CURRENT_POST_IDENTIFIER'), None)
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
            self.add_publish_button()

    def add_copy_language_to_menu(self):
        if self.toolbar.edit_mode:
            language_menu = self.toolbar.get_menu(LANGUAGE_MENU_IDENTIFIER)
            copy_menu_orig = language_menu.menus.pop('{0}-copy'.format(LANGUAGE_MENU_IDENTIFIER))
            language_menu.items.remove(copy_menu_orig)
            admin_menu = self.toolbar.get_or_create_menu('djangocms_blog', _('Blog'))

            languages = get_language_dict(self.current_site.pk)

            add = [l for l in languages.items()]
            copy = [(code, name) for code, name in languages.items() if code != self.current_lang]

            if add or copy:
                admin_menu.add_break(ADD_PAGE_LANGUAGE_BREAK)
            current_post = getattr(self.request, get_setting('CURRENT_POST_IDENTIFIER'), None)
            if current_post and copy:
                copy_plugins_menu = admin_menu.get_or_create_menu('{0}-copy'.format(LANGUAGE_MENU_IDENTIFIER), _('Copy all placeholders'))
                title = _('from %s')
                question = _('Are you sure you want to copy all plugins from %s?')
                page_copy_url = reverse('{}:copy-language-blog'.format(current_post.app_config.namespace), args=(current_post.pk,))
                for code, name in copy:
                    copy_plugins_menu.add_ajax_item(
                        title % name, action=page_copy_url,
                        data={'source_language': code, 'target_language': self.current_lang},
                        question=question % name, on_success=self.toolbar.REFRESH_PAGE
                    )
