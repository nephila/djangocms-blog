from functools import cached_property

from cms.cms_toolbars import ADMIN_MENU_IDENTIFIER, ADMINISTRATION_BREAK, SHORTCUTS_BREAK
from cms.toolbar.items import Break, ButtonList
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _, override
from djangocms_versioning.constants import PUBLISHED

from .models import PostContent, Post
from .settings import get_setting
from .utils import is_versioning_enabled


@toolbar_pool.register
class BlogToolbar(CMSToolbar):
    def _get_published_post_version(self):
        """Returns a published page if one exists for the toolbar object
        """
        language = self.current_lang
        # Exit the current toolbar object is not a Page / PageContent instance
        if not isinstance(self.toolbar.obj, PostContent):
            return

        return PostContent.admin_manager.filter(
            post=self.toolbar.obj.post, language=language, versions__state=PUBLISHED
        ).first()

    def add_view_published_button(self):
        """Helper method to add a publish button to the toolbar
        """
        # Check if object is registered with versioning otherwise don't add
        if not is_versioning_enabled():
            return

        # Add the View published button if in edit or preview mode
        published_version = self._get_published_post_version()
        if not published_version:
            return

        url = published_version.get_absolute_url() if hasattr(published_version, 'get_absolute_url') else None
        if url and (self.toolbar.edit_mode_active or self.toolbar.preview_mode_active):
            item = ButtonList(side=self.toolbar.RIGHT)
            item.add_button(
                _("View Published"),
                url=url,
                disabled=False,
                extra_classes=['cms-btn', 'cms-btn-switch-save'],
            )
            self.toolbar.add_item(item)

    def add_blog_to_admin_menu(self):
        admin_menu = self.toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)
        print(f"--> {admin_menu}")
        url = reverse("admin:djangocms_blog_post_changelist")
        admin_menu.add_sideframe_item(
            Post._meta.verbose_name_plural.capitalize(),
            url=url,
            position=self.get_insert_position_for_admin_object(admin_menu, Post._meta.verbose_name_plural.capitalize()),
        )

    def populate(self):
        self.add_blog_to_admin_menu()
        is_current_app = self.is_current_app or isinstance(self.toolbar.get_object(), PostContent)
        if (
            not is_current_app and not get_setting("ENABLE_THROUGH_TOOLBAR_MENU")
        ) or not self.request.user.has_perm("djangocms_blog.add_post"):
            return  # pragma: no cover
        admin_menu = self.toolbar.get_or_create_menu("djangocms_blog", _("Blog"))
        with override(self.current_lang):
            url = reverse("admin:djangocms_blog_post_add")
            admin_menu.add_modal_item(_("Create post"), url=url)
            current_config = getattr(self.request, get_setting("CURRENT_NAMESPACE"), None)
            if current_config:
                url = reverse("admin:djangocms_blog_blogconfig_change", args=(current_config.pk,))
                admin_menu.add_modal_item(_("Edit configuration"), url=url)

            current_post = getattr(self.request, get_setting("CURRENT_POST_IDENTIFIER"), None)
            if current_post and self.request.user.has_perm("djangocms_blog.change_post"):  # pragma: no cover  # NOQA
                admin_menu.add_modal_item(
                    _("Edit Post"), reverse("admin:djangocms_blog_post_change", args=(current_post.pk,)),
                )
        self.add_view_published_button()  # Takes the user the published post version

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

    @staticmethod
    def get_insert_position_for_admin_object(admin_menu, item_name):
        """
        gets canonical position of admin object leaving the Page entry at
        first position, Administration entry at last position and sorting
        alphabetically until the ADMINISTRATION_BREAK.
        """
        end = admin_menu.find_first(Break, identifier=ADMINISTRATION_BREAK)
        if end.index < 2:
            return end.index

        items = admin_menu.get_items()[1: end.index - 1]
        for idx, item in enumerate(items):
            try:
                if force_str(item_name.lower()) < force_str(item.name.lower()):  # noqa: E501
                    return idx + 1
            except AttributeError:
                # Some item types do not have a 'name' attribute.
                pass
        return end.index
