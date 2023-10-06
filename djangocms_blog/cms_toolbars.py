from cms.cms_toolbars import ADMIN_MENU_IDENTIFIER, ADMINISTRATION_BREAK, SHORTCUTS_BREAK
from cms.models import PageContent
from cms.toolbar.items import Break, ButtonList
from cms.toolbar.utils import get_object_preview_url
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _, override
from djangocms_versioning.constants import PUBLISHED

from .models import Post, PostContent
from .settings import get_setting
from .utils import is_versioning_enabled


@toolbar_pool.register
class BlogToolbar(CMSToolbar):
    def _get_published_post_version(self):
        """Returns a published page if one exists for the toolbar object"""
        language = self.current_lang
        # Exit the current toolbar object is not a Page / PageContent instance
        if not isinstance(self.toolbar.obj, PostContent):
            return

        return PostContent.admin_manager.filter(
            post=self.toolbar.obj.post, language=language, versions__state=PUBLISHED
        ).first()

    def add_preview_button(self):
        if self.is_current_app and self.toolbar.get_object() is None:
            # TODO: Restrict preview button to root url of blog
            page_content = self.request.current_page.pagecontent_set(manager="admin_manager").latest_content().first()
            url = get_object_preview_url(page_content, language=self.toolbar.request_language)
            item = ButtonList(side=self.toolbar.RIGHT)
            if self.toolbar.preview_mode_active:
                print(f"==> {self.request.path_info=} {self.toolbar.request_path=}")
                item.add_button(
                    _("View on site"),
                    url=page_content.get_absolute_url(),
                    disabled=False,
                    extra_classes=["cms-btn", "cms-btn-switch-save"],
                )
            else:
                item.add_button(
                    _("Preview"),
                    url=url,
                    disabled=False,
                    extra_classes=["cms-btn", "cms-btn-switch-save"],
                )
            self.toolbar.add_item(item)

    def add_view_published_button(self):
        """Helper method to add a publish button to the toolbar"""
        # Check if object is registered with versioning otherwise don't add
        if not is_versioning_enabled():
            return

        # Add the View published button if in edit or preview mode
        published_version = self._get_published_post_version()
        if not published_version:
            return

        url = published_version.get_absolute_url() if hasattr(published_version, "get_absolute_url") else None
        if url and (self.toolbar.edit_mode_active or self.toolbar.preview_mode_active):
            item = ButtonList(side=self.toolbar.RIGHT)
            item.add_button(
                _("View Published"),
                url=url,
                disabled=False,
                extra_classes=["cms-btn", "cms-btn-switch-save"],
            )
            self.toolbar.add_item(item)

    def add_blog_to_admin_menu(self):
        admin_menu = self.toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)
        url = admin_reverse("djangocms_blog_post_changelist")
        admin_menu.add_sideframe_item(
            Post._meta.verbose_name_plural.capitalize(),
            url=url,
            position=self.get_insert_position_for_admin_object(
                admin_menu,
                Post._meta.verbose_name_plural.capitalize(),
            ),
        )

    def populate(self):
        self.add_blog_to_admin_menu()
        # Add on apphook urls and endpoint urls
        is_current_app = self.is_current_app or isinstance(self.toolbar.get_object(), PostContent)
        if (not is_current_app and not get_setting("ENABLE_THROUGH_TOOLBAR_MENU")) or not self.request.user.has_perm(
            "djangocms_blog.add_post"
        ):
            return  # pragma: no cover

        current_content = getattr(self.request, get_setting("CURRENT_POST_IDENTIFIER"), self.toolbar.get_object())
        current_config = getattr(
            self.request, get_setting("CURRENT_NAMESPACE"), current_content.app_config if current_content else None
        )
        with override(self.current_lang):
            menu_name = _("Blog")
            if current_config and current_config.app_title:
                menu_name = current_config.app_title.capitalize()
            admin_menu = self.toolbar.get_or_create_menu("djangocms_blog", menu_name)
            object_name = current_config.object_name if current_config else Post._meta.verbose_name
            if current_content and self.request.user.has_perm("djangocms_blog.change_post"):
                admin_menu.add_modal_item(
                    _("%(object_name)s properties") % dict(object_name=object_name.capitalize()),
                    admin_reverse("djangocms_blog_post_change", args=(current_content.post.pk,)),
                )
            url = admin_reverse("djangocms_blog_post_add")
            if current_config:
                url += f"?app_config={current_config.pk}"
            admin_menu.add_modal_item(
                _("Create %(object_name)s") % dict(object_name=object_name),
                url=url,
            )
            if current_config:
                url = admin_reverse("djangocms_blog_blogconfig_change", args=(current_config.pk,))
                admin_menu.add_modal_item(_("Edit configuration"), url=url)
        self.add_preview_button()
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

        items = admin_menu.get_items()[1 : end.index - 1]
        for idx, item in enumerate(items):
            try:
                if force_str(item_name.lower()) < force_str(item.name.lower()):  # noqa: E501
                    return idx + 1
            except AttributeError:
                # Some item types do not have a 'name' attribute.
                pass
        return end.index

    @staticmethod
    def get_insert_position_for_admin_objectx(admin_menu, item_name):
        """
        Ensures that there is a SHORTCUTS_BREAK and returns a position for an
        alphabetical position against all items between SHORTCUTS_BREAK, and
        the ADMINISTRATION_BREAK.
        """
        start = admin_menu.find_first(Break, identifier=SHORTCUTS_BREAK)

        if not start:
            end = admin_menu.find_first(Break, identifier=ADMINISTRATION_BREAK)
            admin_menu.add_break(SHORTCUTS_BREAK, position=end.index)
            start = admin_menu.find_first(Break, identifier=SHORTCUTS_BREAK)
        end = admin_menu.find_first(Break, identifier=ADMINISTRATION_BREAK)

        items = admin_menu.get_items()[start.index + 1 : end.index]
        for idx, item in enumerate(items):
            try:
                if force_str(item_name.lower()) < force_str(item.name.lower()):  # noqa: E501
                    return idx + start.index + 1
            except AttributeError:
                # Some item types do not have a 'name' attribute.
                pass
        return end.index
