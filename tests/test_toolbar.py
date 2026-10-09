from cms.toolbar.items import ButtonList, ModalItem
from django.urls import reverse
from django.utils.encoding import force_str

from djangocms_blog.compat import CMS_4_PLUS
from djangocms_blog.models import BLOG_CURRENT_POST_IDENTIFIER

from .base import BaseTest


class ToolbarTest(BaseTest):
    def test_toolbar_with_items(self):
        """
        Test that Blog toolbar is present and contains all items
        """
        from cms.toolbar.toolbar import CMSToolbar

        pages = self.get_pages()
        posts = self.get_posts()
        request = self.get_page_request(pages[0], self.user, r"/en/blog/", edit=True)
        setattr(request, BLOG_CURRENT_POST_IDENTIFIER, posts[0])

        posts[0].publish = False
        posts[0].save()
        toolbar = CMSToolbar(request)
        # django CMS 3.x compatibility: in CMS 4.x edit_mode_active is a cached_property
        # that no longer activates from the ?edit URL param; must be forced manually.
        # When CMS 3.x support is dropped, remove the `if CMS_4_PLUS:` guards and
        # always set toolbar.__dict__["edit_mode_active"] = True (or update the test
        # to use the CMS 4.x edit activation mechanism).
        if CMS_4_PLUS:
            toolbar.__dict__["edit_mode_active"] = True
        toolbar.populate()
        toolbar.post_template_populate()
        toolbar.get_left_items()
        blog_menu = toolbar.menus["djangocms_blog"]
        self.assertEqual(len(blog_menu.find_items(ModalItem, url=reverse("admin:djangocms_blog_post_changelist"))), 1)
        self.assertEqual(
            len(blog_menu.find_items(ModalItem, url=reverse("admin:djangocms_blog_blogcategory_changelist"))),
            1,
        )
        self.assertEqual(len(blog_menu.find_items(ModalItem, url=reverse("admin:taggit_tag_changelist"))), 1)
        self.assertEqual(len(blog_menu.find_items(ModalItem, url=reverse("admin:djangocms_blog_post_add"))), 1)
        self.assertEqual(
            len(blog_menu.find_items(ModalItem, url=reverse("admin:djangocms_blog_post_change", args=(posts[0].pk,)))),
            1,
        )

        # Publish button only appears if current post is unpublished
        right = toolbar.get_right_items()
        buttons = sum((item.buttons for item in right if isinstance(item, ButtonList)), [])
        self.assertTrue([button for button in buttons if force_str(button.name) == "Publish Blog now"])

        # Publish button does not appears if current post is published
        posts[0].publish = True
        posts[0].save()
        toolbar = CMSToolbar(request)
        if CMS_4_PLUS:  # django CMS 3.x compatibility: see comment above
            toolbar.__dict__["edit_mode_active"] = True
        toolbar.populate()
        toolbar.post_template_populate()
        right = toolbar.get_right_items()
        buttons = sum((item.buttons for item in right if isinstance(item, ButtonList)), [])
        self.assertFalse([button for button in buttons if force_str(button.name) == "Publish Blog now"])

        # Publish button does not appears if other posts but the current one are unpublished
        posts[1].publish = True
        posts[1].save()
        toolbar = CMSToolbar(request)
        if CMS_4_PLUS:  # django CMS 3.x compatibility: see comment above
            toolbar.__dict__["edit_mode_active"] = True
        toolbar.populate()
        toolbar.post_template_populate()
        right = toolbar.get_right_items()
        buttons = sum((item.buttons for item in right if isinstance(item, ButtonList)), [])
        self.assertFalse([button for button in buttons if force_str(button.name) == "Publish Blog now"])
