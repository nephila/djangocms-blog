from contextlib import contextmanager

from cms.api import create_page
from django.test import Client
from django.utils.encoding import force_str

from djangocms_blog.cms_appconfig import BlogConfig

from .base import BaseTest
from .test_utils.models import CustomUser as User

try:
    from knocker.signals import pause_knocks
except ImportError:

    @contextmanager
    def pause_knocks(obj):
        yield


class AdminTest(BaseTest):
    def setUp(self):
        User.objects.create_superuser("test_admin", "admin@example.com", "Password123")

    def add_blog_config(self, page, namespace, id):
        self.client = Client()
        self.client.login(username="test_admin", password="Password123")
        response = self.client.post(
            "/en/admin/cms/page/{}/advanced-settings/?language=en".format(page.pk),
            {
                "language": "nl",
                "overwrite_url": "",
                "redirect": "",
                "template": "blog.html",
                "reverse_id": "",
                "navigation_extenders": "",
                "application_urls": "BlogApp",
                "application_namespace": namespace,
                "application_configs": id,
                "xframe_options": "0",
                "_save": "Save",
            },
            follow=True,
        )
        self.client.logout()
        return response

    def test_add_blog_config(self):
        """
        Adjust advanced settings of a page with blog config create.
        """
        self.assertEqual(BlogConfig.objects.count(), 2)

        page = create_page("Blog", "blog.html", "en", published=True)
        self.add_blog_config(page, "Blog", 1)
        response = self.add_blog_config(page, "Blog", 1)
        content = force_str(response.content)
        self.assertNotRegex(content, r"Please correct the error below.")
        self.assertEqual(BlogConfig.objects.count(), 2)

        response = self.client.get("/en/blog/")
        content = force_str(response.content)
        self.assertRegex(content, r"No article found.")

        page = create_page("Blog2", "blog.html", "en", published=True)
        response = self.add_blog_config(page, "Blog2", "")
        content = force_str(response.content)
        self.assertNotRegex(content, r"Please correct the error below.")
        self.assertNotRegex(content, r"An application instance using this configuration already exists.")

        response = self.client.get("/en/blog2/")
        content = force_str(response.content)
        self.assertRegex(content, r"Blog2")
