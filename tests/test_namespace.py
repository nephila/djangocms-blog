from contextlib import contextmanager

from cms.api import create_page
from django.test import Client
from django.utils.encoding import force_str

from .base import BaseTest

try:
    from knocker.signals import pause_knocks
except ImportError:

    @contextmanager
    def pause_knocks(obj):
        yield


class AdminTest(BaseTest):
    def add_blog_config(self, page, namespace, config_id):
        self.client = Client()
        self.client.login(username=self._admin_user_username, password=self._admin_user_password)
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
                "application_configs": config_id,
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
        page = create_page("Blog2", "blog.html", "en", published=True)
        response = self.add_blog_config(page, "Blog2", "")
        content = force_str(response.content)
        self.assertNotRegex(content, r"Please correct the error below.")
        self.assertNotRegex(content, r"An application instance using this configuration already exists.")

        response = self.client.get("/en/blog2/")
        content = force_str(response.content)
        self.assertRegex(content, r"Blog2")
