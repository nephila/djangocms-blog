import sys

from cms.api import create_page, create_title
from cms.models import Page
from cms.utils import get_language_list
from django.utils.translation import override

from djangocms_blog.cms_appconfig import BlogConfig

from .base import BaseTest

try:
    from django.test import override_settings
except ImportError:
    from django.test.utils import override_settings


@override_settings(BLOG_AUTO_SETUP=True)
class SetupTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        # Skipping initialization to start with clean database
        super(BaseTest, cls).setUpClass()

    def setUp(self):
        super().setUp()
        from cms.apphook_pool import apphook_pool

        delete = [
            "djangocms_blog",
            "djangocms_blog.cms_app",
            "djangocms_blog.cms_apps",
        ]
        for module in delete:
            if module in sys.modules:
                del sys.modules[module]
        BlogConfig.cmsapp = None
        apphook_pool.clear()

    def test_setup_from_url(self):
        # Tests starts with no page and no config
        self.assertFalse(Page.objects.exists())
        self.assertFalse(BlogConfig.objects.exists())

        # importing cms_app triggers the auto setup
        from djangocms_blog import cms_apps  # NOQA

        # Home and blog, published and draft
        self.assertEqual(Page.objects.count(), 4)
        self.assertEqual(BlogConfig.objects.count(), 1)

    def test_setup_filled(self):
        # Tests starts with no page and no config
        self.assertFalse(Page.objects.exists())
        self.assertFalse(BlogConfig.objects.exists())
        set_home = hasattr(Page, "set_as_homepage")

        langs = get_language_list()
        home = None
        for lang in langs:
            with override(lang):
                if not home:
                    home = create_page(
                        "a new home", language=lang, template="blog.html", in_navigation=True, published=True
                    )
                    if set_home:
                        home.set_as_homepage()
                else:
                    create_title(language=lang, title="a new home", page=home)
                    home.publish(lang)

        # importing cms_app triggers the auto setup
        from djangocms_blog import cms_apps  # NOQA

        # Home and blog, published and draft
        self.assertEqual(Page.objects.count(), 4)
        self.assertEqual(BlogConfig.objects.count(), 1)

        home = Page.objects.get_home()
        for lang in langs:
            self.assertEqual(home.get_title(lang), "a new home")
