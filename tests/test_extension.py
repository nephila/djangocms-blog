from cms.api import add_plugin
from django.contrib import admin
from django.utils.encoding import force_str

import djangocms_blog.admin
from djangocms_blog.models import Post

from .base import BaseTest
from .test_utils.admin import PostExtensionInline
from .test_utils.models import PostPlaceholderExtension


class AddExtensionTest(BaseTest):
    def test_register_inline_extension(self):
        djangocms_blog.admin.register_extension(PostExtensionInline)
        djangocms_blog.admin.unregister_extension(PostExtensionInline)

    def test_register_placeholder_extension(self):
        djangocms_blog.admin.register_extension(PostPlaceholderExtension)
        djangocms_blog.admin.unregister_extension(PostPlaceholderExtension)

    def test_register_placeholder_extension_twice(self):
        djangocms_blog.admin.register_extension(PostPlaceholderExtension)
        with self.assertRaises(Exception):  # noqa: B017
            djangocms_blog.admin.register_extension(PostPlaceholderExtension)
        djangocms_blog.admin.unregister_extension(PostPlaceholderExtension)
        with self.assertRaises(Exception):  # noqa: B017
            djangocms_blog.admin.unregister_extension(PostPlaceholderExtension)

    def test_register_other(self):
        class X:
            pass

        with self.assertRaises(Exception):  # noqa: B017
            djangocms_blog.admin.register_extension(X)
        with self.assertRaises(Exception):  # noqa: B017
            djangocms_blog.admin.register_extension(X)

    def test_placeholder_object_auto_created(self):
        PostPlaceholderExtension.objects.all().delete()
        djangocms_blog.admin.register_extension(PostPlaceholderExtension)
        post = self._get_post(self._post_data[0]["en"])
        PostPlaceholderExtension.objects.get(post=post)
        post.delete()
        djangocms_blog.admin.unregister_extension(PostPlaceholderExtension)

    def test_add_plugin_to_placeholder(self):
        djangocms_blog.admin.register_extension(PostPlaceholderExtension)
        pages = self.get_pages()
        try:
            # django CMS 3.x compatibility: Page.placeholders M2M removed in CMS 4.x
            ph = pages[0].placeholders.get(slot="some_placeholder")
        except AttributeError:  # CMS 4.x: no placeholders M2M field
            ph = pages[0].get_placeholders("en").get(slot="some_placeholder")
        plugin = add_plugin(ph, "TextPlugin", language="en", body="<p>test</p>")
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertTrue(rendered.find("<p>test</p>") > -1)
        for page in pages:
            page.delete()
        djangocms_blog.admin.unregister_extension(PostPlaceholderExtension)

    def test_admin_post_views_should_have_extension(self):
        djangocms_blog.admin.register_extension(PostExtensionInline)

        self.get_pages()

        post_admin = admin.site._registry[Post]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)

        post = self._get_post(self._post_data[0]["en"])

        # Add view should contain extension
        response = post_admin.add_view(request)
        response.render()
        # Django 5.x compatibility: admin inline headings now use
        # <h2 id="..." class="inline-heading"> instead of bare <h2>.
        # When Django 4.x support is dropped, the regex can be simplified back to r"<h2>.*PostExtension.*</h2>".
        self.assertRegex(force_str(response.content), r"<h2[^>]*>[\s\S]*?PostExtension")

        # Changeview should contain extension
        response = post_admin.change_view(request, str(post.pk))
        response.render()
        self.assertRegex(force_str(response.content), r"<h2[^>]*>[\s\S]*?PostExtension")
        post.delete()
        djangocms_blog.admin.unregister_extension(PostExtensionInline)

    def test_admin_post_views_should_not_have_extension(self):
        djangocms_blog.admin.register_extension(PostExtensionInline)
        djangocms_blog.admin.unregister_extension(PostExtensionInline)

        self.get_pages()

        post_admin = admin.site._registry[Post]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)

        post = self._get_post(self._post_data[0]["en"])

        # Add view should contain extension
        response = post_admin.add_view(request)
        response.render()
        # Django 5.x compatibility: see comment in test_admin_post_views_should_have_extension
        self.assertNotRegex(force_str(response.content), r"<h2[^>]*>[\s\S]*?PostExtension")

        # Changeview should contain extension
        response = post_admin.change_view(request, str(post.pk))
        response.render()
        self.assertNotRegex(force_str(response.content), r"<h2[^>]*>[\s\S]*?PostExtension")
        post.delete()
