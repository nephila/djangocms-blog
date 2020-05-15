from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, override

from .settings import get_setting


@toolbar_pool.register
class BlogToolbar(CMSToolbar):
    def populate(self):
        if (
            not self.is_current_app and not get_setting("ENABLE_THROUGH_TOOLBAR_MENU")
        ) or not self.request.user.has_perm("djangocms_blog.add_post"):
            return  # pragma: no cover
        admin_menu = self.toolbar.get_or_create_menu("djangocms_blog", _("Blog"))
        with override(self.current_lang):
            url = reverse("admin:djangocms_blog_post_changelist")
            admin_menu.add_modal_item(_("Post list"), url=url)
            url = reverse("admin:djangocms_blog_post_add")
            admin_menu.add_modal_item(_("Add post"), url=url)
            current_config = getattr(self.request, get_setting("CURRENT_NAMESPACE"), None)
            if current_config:
                url = reverse("admin:djangocms_blog_blogconfig_change", args=(current_config.pk,))
                admin_menu.add_modal_item(_("Edit configuration"), url=url)

            current_post = getattr(self.request, get_setting("CURRENT_POST_IDENTIFIER"), None)
            if current_post and self.request.user.has_perm("djangocms_blog.change_post"):  # pragma: no cover  # NOQA
                admin_menu.add_modal_item(
                    _("Edit Post"), reverse("admin:djangocms_blog_post_change", args=(current_post.pk,)), active=True
                )

    def add_publish_button(self):
        """
        Adds the publish button to the toolbar if the current post is unpublished
        """
        current_post = getattr(self.request, get_setting("CURRENT_POST_IDENTIFIER"), None)
        if (
            self.toolbar.edit_mode_active
            and current_post
            and not current_post.publish
            and self.request.user.has_perm("djangocms_blog.change_post")
        ):  # pragma: no cover  # NOQA
            classes = ["cms-btn-action", "blog-publish"]
            title = _("Publish {0} now").format(current_post.app_config.object_name)

            url = admin_reverse("djangocms_blog_publish_article", args=(current_post.pk,))

            self.toolbar.add_button(title, url=url, extra_classes=classes, side=self.toolbar.RIGHT)

    def post_template_populate(self):
        current_post = getattr(self.request, get_setting("CURRENT_POST_IDENTIFIER"), None)
        if current_post and self.request.user.has_perm("djangocms_blog.change_post"):  # pragma: no cover  # NOQA
            # removing page meta menu, if present, to avoid confusion
            try:  # pragma: no cover
                import djangocms_page_meta  # NOQA

                menu = self.request.toolbar.get_or_create_menu("page")
                pagemeta = menu.get_or_create_menu("pagemeta", "meta")
                menu.remove_item(pagemeta)
            except ImportError:
                pass
            # removing page tags menu, if present, to avoid confusion
            try:  # pragma: no cover
                import djangocms_page_tags  # NOQA

                menu = self.request.toolbar.get_or_create_menu("page")
                pagetags = menu.get_or_create_menu("pagetags", "tags")
                menu.remove_item(pagetags)
            except ImportError:
                pass
            self.add_publish_button()
