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
        ph = pages[0].placeholders.get(slot="some_placeholder")
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
        self.assertRegex(force_str(response.content), r"<h2>.*PostExtension.*</h2>")

        # Changeview should contain extension
        response = post_admin.change_view(request, str(post.pk))
        response.render()
        self.assertRegex(force_str(response.content), r"<h2>.*PostExtension.*</h2>")
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
        self.assertNotRegex(force_str(response.content), r"<h2>.*PostExtension.*</h2>")

        # Changeview should contain extension
        response = post_admin.change_view(request, str(post.pk))
        response.render()
        self.assertNotRegex(force_str(response.content), r"<h2>.*PostExtension.*</h2>")
        post.delete()
