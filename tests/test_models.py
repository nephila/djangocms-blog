import re
from contextlib import contextmanager
from copy import deepcopy
from datetime import timedelta
from unittest import SkipTest
from urllib.parse import quote

import parler
from cms.api import add_plugin
from cms.utils.copy_plugins import copy_plugins_to
from cms.utils.plugins import downcast_plugins
from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sites.models import Site
from django.core.handlers.base import BaseHandler
from django.http import QueryDict
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.html import strip_tags
from django.utils.timezone import now
from django.utils.translation import get_language, override
from easy_thumbnails.files import get_thumbnailer
from filer.models import ThumbnailOption
from menus.menu_pool import menu_pool
from parler.tests.utils import override_parler_settings
from parler.utils.conf import add_default_language_settings
from parler.utils.context import smart_override
from taggit.models import Tag

from djangocms_blog.cms_appconfig import BlogConfig, BlogConfigForm
from djangocms_blog.forms import CategoryAdminForm, PostAdminForm
from djangocms_blog.models import BlogCategory, Post
from djangocms_blog.settings import MENU_TYPE_NONE, PERMALINK_TYPE_CATEGORY, PERMALINK_TYPE_FULL_DATE, get_setting

from .base import BaseTest
from .test_utils.admin import CustomPostAdmin

try:
    from knocker.signals import pause_knocks
except ImportError:

    @contextmanager
    def pause_knocks(obj):
        yield


class AdminTest(BaseTest):
    def setUp(self):
        super().setUp()
        admin.autodiscover()
        self.default_thumbnail = ThumbnailOption.objects.create(
            name="Blog thumbnail",
            width=120,
            height=120,
            crop=True,
            upscale=True,
        )
        self.default_full = ThumbnailOption.objects.create(
            name="Blog image",
            width=800,
            height=200,
            crop=True,
            upscale=True,
        )

    def test_admin_thumbnails(self):
        self.get_pages()

        custom_thumbnail = ThumbnailOption.objects.create(
            name="Custom thumbnail",
            width=120,
            height=120,
            crop=True,
            upscale=True,
        )
        custom_full = ThumbnailOption.objects.create(
            name="Custom image",
            width=800,
            height=200,
            crop=True,
            upscale=True,
        )

        post_admin = admin.site._registry[Post]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)

        post = self._get_post(self._post_data[0]["en"])
        post = self._get_post(self._post_data[0]["it"], post, "it")

        response = post_admin.change_view(request, str(post.pk))
        response.render()
        self.assertRegex(force_str(response.content), r"[^>]*>Custom image")
        self.assertRegex(force_str(response.content), r"[^>]*>Custom thumbnail")
        self.assertRegex(force_str(response.content), r"[^>]*>Blog image")
        self.assertRegex(force_str(response.content), r"[^>]*>Blog thumbnail")

        post.main_image_full = custom_full
        post.main_image_thumbnail = custom_thumbnail
        post.save()
        response = post_admin.change_view(request, str(post.pk))
        response.render()
        self.assertRegex(force_str(response.content), r"selected[^>]*>Custom image")
        self.assertRegex(force_str(response.content), r"selected[^>]*>Custom thumbnail")

        self.app_config_1.app_data.config.default_image_full = self.default_full
        self.app_config_1.app_data.config.default_image_thumbnail = self.default_thumbnail
        self.app_config_1.save()
        post.main_image_full = None
        post.main_image_thumbnail = None
        post.save()

        response = post_admin.change_view(request, str(post.pk))
        response.render()
        self.assertRegex(force_str(response.content), r"selected[^>]*>Blog image")
        self.assertRegex(force_str(response.content), r"selected[^>]*>Blog thumbnail")

    def test_admin_category_required(self):
        self.get_pages()

        post_admin = admin.site._registry[Post]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)
        BlogCategory.objects.create(name="category 1 - blog 2", app_config=self.app_config_2)

        post = self._get_post(self._post_data[0]["en"])
        post = self._get_post(self._post_data[0]["it"], post, "it")

        response = post_admin.change_view(request, str(post.pk))
        self.assertEqual(
            response.context_data["adminform"].form.fields["categories"].required,
            self.app_config_1.url_patterns == PERMALINK_TYPE_CATEGORY,
        )

        self.app_config_1.app_data.config.url_patterns = PERMALINK_TYPE_CATEGORY
        self.app_config_1.save()

        response = post_admin.change_view(request, str(post.pk))
        self.assertEqual(
            response.context_data["adminform"].form.fields["categories"].required,
            self.app_config_1.url_patterns == PERMALINK_TYPE_CATEGORY,
        )

        self.app_config_1.app_data.config.url_patterns = PERMALINK_TYPE_FULL_DATE
        self.app_config_1.save()

    def test_admin_post_views(self):
        self.get_pages()

        post_admin = admin.site._registry[Post]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)

        post = self._get_post(self._post_data[0]["en"])
        post = self._get_post(self._post_data[0]["it"], post, "it")

        # Add view only contains the apphook selection widget
        response = post_admin.add_view(request)
        self.assertNotContains(response, '<input id="id_slug" maxlength="752" name="slug" type="text"')
        self.assertContains(response, '<option value="%s">Blog / sample_app</option>' % self.app_config_1.pk)

        # Changeview is 'normal'
        response = post_admin.change_view(request, str(post.pk))
        response.render()
        try:
            self.assertRegex(force_str(response.content), r'name="slug"[^>]*value="first-post"')
        except AssertionError:
            self.assertRegex(force_str(response.content), r'value="first-post"[^>]*name="slug"')
        try:
            self.assertRegex(force_str(response.content), r'id="id_meta_description"[^>]*maxlength="320"')
        except AssertionError:
            self.assertRegex(force_str(response.content), r'maxlength="320"[^>]*id="id_meta_description"')
        try:
            self.assertRegex(
                force_str(response.content),
                r'selected[^>]*value="%s">Blog / sample_app</option>' % self.app_config_1.pk,
            )
        except AssertionError:
            self.assertRegex(
                force_str(response.content),
                r'value="%s"[^>]*selected[^>]*>Blog / sample_app</option>' % self.app_config_1.pk,
            )

        # Test for publish view
        post.publish = False
        post.save()
        response = post_admin.publish_post(request, str(post.pk))
        # Redirects to current post
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], post.get_absolute_url())
        post = self.reload_model(post)
        # post is publshed
        self.assertTrue(post.publish)

        # Non-existing post is redirected to posts list
        response = post_admin.publish_post(request, "1000000")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("djangocms_blog:posts-latest"))

        # unless a referer is set
        request.META["HTTP_REFERER"] = "/"
        # reset headers cached property
        del request.headers
        response = post_admin.publish_post(request, "1000000")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

    def test_admin_post_delete(self):
        self.get_pages()

        post_admin = admin.site._registry[Post]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)

        post = self._get_post(self._post_data[0]["en"])
        post = self._get_post(self._post_data[0]["it"], post, "it")

        post_admin.delete_model(request, post)

    def test_admin_post_delete_queryset(self):
        self.get_pages()

        post_admin = admin.site._registry[Post]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)

        post_admin.delete_queryset(request, post_admin.get_queryset(request))

    def test_admin_changelist_view(self):
        self.get_pages()

        posts = self.get_posts()
        post_admin = admin.site._registry[Post]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)

        # Normal changelist, all existing posts
        response = post_admin.changelist_view(request)
        self.assertEqual(response.context_data["cl"].queryset.count(), len(posts))
        self.assertTrue(posts[0] in response.context_data["cl"].queryset.all())

        # Site 2 is added to first post, but no changelist filter, no changes
        posts[0].sites.add(self.site_2)
        response = post_admin.changelist_view(request)
        self.assertTrue(posts[0] in response.context_data["cl"].queryset.all())

        # Filtering on site, first post not shown
        request = self.get_page_request("/", self.user, r"/en/blog/?sites=1", edit=False)
        response = post_admin.changelist_view(request)
        self.assertEqual(response.context_data["cl"].queryset.count(), len(posts) - 1)
        self.assertTrue(posts[0] not in response.context_data["cl"].queryset.all())

        # Removing site filtering, first post appears again
        request = self.get_page_request("/", self.user, r"/en/blog/?", edit=False)
        response = post_admin.changelist_view(request)
        self.assertEqual(response.context_data["cl"].queryset.count(), len(posts))
        self.assertTrue(posts[0] in response.context_data["cl"].queryset.all())

        # Filtering on the apphook config and site
        request = self.get_page_request(
            "/", self.user, r"/en/blog/?app_config__id__exact=%s&sites=1" % self.app_config_1.pk, edit=False
        )
        response = post_admin.changelist_view(request)
        # First and last post in the list are now in the queryset
        self.assertEqual(response.context_data["cl"].queryset.count(), len(posts) - 2)
        self.assertTrue(posts[0] not in response.context_data["cl"].queryset.all())
        self.assertTrue(posts[-1] not in response.context_data["cl"].queryset.all())

        # Publishing one post, two published in total
        posts[1].publish = True
        posts[1].save()
        published = Post.objects.published(current_site=False)
        request = self.get_page_request("/", self.user, r"/en/blog/?publish__exact=1", edit=False)
        response = post_admin.changelist_view(request)
        # The admin queryset and the model queryset are the same
        self.assertEqual(response.context_data["cl"].queryset.count(), published.count())
        # Published post is in the changelist queryset
        self.assertTrue(posts[1] in response.context_data["cl"].queryset.all())

    def test_admin_blogconfig_views(self):
        post_admin = admin.site._registry[BlogConfig]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)

        # Add view only has an empty form - no type
        response = post_admin.add_view(request)
        response.render()
        self.assertNotContains(response, "djangocms_blog.cms_appconfig.BlogConfig")
        try:
            self.assertRegex(force_str(response.content), r'maxlength="100"[^>]*id="id_namespace"')
        except AssertionError:
            self.assertRegex(force_str(response.content), r'id="id_namespace"[^>]*maxlength="100"')

        # Changeview is 'normal', with a few preselected items
        response = post_admin.change_view(request, str(self.app_config_1.pk))
        self.assertContains(response, "djangocms_blog.cms_appconfig.BlogConfig")
        try:
            self.assertRegex(force_str(response.content), r'selected[^>]*value="Article">Article')
        except AssertionError:
            self.assertRegex(force_str(response.content), r'value="Article"[^>]*selected[^>]*>Article')
        # check that all the form fields are visible in the admin
        for fieldname in BlogConfigForm.base_fields:
            self.assertContains(response, 'id="id_config-%s"' % fieldname)
        try:
            self.assertRegex(force_str(response.content), r'maxlength="200"[^>]*id="id_config-og_app_id"')
        except AssertionError:
            self.assertRegex(force_str(response.content), r'id="id_config-og_app_id"[^>]*maxlength="200"')

        self.assertContains(response, "sample_app")

    def test_admin_category_views(self):
        category_admin = admin.site._registry[BlogCategory]
        request = self.get_page_request("/", self.user, r"/en/blog/", edit=False)
        BlogCategory.objects.create(name="category 1 - blog 2", app_config=self.app_config_2)

        # Add view only has an empty form - no type
        response = category_admin.add_view(request)
        self.assertNotContains(response, 'value="category 1"')
        self.assertContains(response, '<option value="%s">Blog / sample_app</option>' % self.app_config_1.pk)

        # Add view select categories on the given appconfig, even when reloading the form
        request.POST = QueryDict("app_config=%s" % self.app_config_1.pk)
        request.method = "POST"
        response = category_admin.add_view(request)
        self.assertEqual(
            list(response.context_data["adminform"].form.fields["parent"].queryset),
            list(BlogCategory.objects.filter(app_config=self.app_config_1)),
        )

        request.GET = QueryDict("app_config=%s" % self.app_config_1.pk)
        request.method = "GET"
        response = category_admin.add_view(request)
        self.assertEqual(
            list(response.context_data["adminform"].form.fields["parent"].queryset),
            list(BlogCategory.objects.filter(app_config=self.app_config_1)),
        )

        # Changeview is 'normal', with a few preselected items
        request.GET = QueryDict()
        response = category_admin.change_view(request, str(self.category_1.pk))
        response.render()
        try:
            self.assertRegex(force_str(response.content), r'id="id_name"[^>]*value="category 1"')
        except AssertionError:
            self.assertRegex(force_str(response.content), r'value="category 1"[^>]*id="id_name"')
        try:
            self.assertRegex(force_str(response.content), r'id="id_meta_description"[^>]*maxlength="320"')
        except AssertionError:
            self.assertRegex(force_str(response.content), r'maxlength="320"[^>]*id="id_meta_description"')
        try:
            self.assertRegex(
                force_str(response.content),
                r'selected[^>]*value="%s">Blog / sample_app</option>' % self.app_config_1.pk,
            )
        except AssertionError:
            self.assertRegex(
                force_str(response.content),
                r'value="%s"[^>]*selected[^>]*>Blog / sample_app</option>' % self.app_config_1.pk,
            )

    def test_form(self):
        posts = self.get_posts()
        with override_settings(BLOG_META_DESCRIPTION_LENGTH=20, BLOG_META_TITLE_LENGTH=20):
            form = PostAdminForm(data={"meta_description": "major text over 20 characters long"}, instance=posts[0])
            self.assertFalse(form.is_valid())
            form = PostAdminForm(data={"meta_title": "major text over 20 characters long"}, instance=posts[0])
            self.assertFalse(form.is_valid())
            form = CategoryAdminForm(
                data={"meta_description": "major text over 20 characters long"}, instance=self.category_1
            )
            self.assertFalse(form.is_valid())

            form = PostAdminForm(data={"meta_description": "mini text"}, instance=posts[0])
            self.assertFalse(form.is_valid())
            form = PostAdminForm(data={"meta_title": "mini text"}, instance=posts[0])
            self.assertFalse(form.is_valid())
            form = CategoryAdminForm(data={"meta_description": "mini text"}, instance=self.category_1)
            self.assertFalse(form.is_valid())

    def test_admin_category_parents(self):
        category1 = BlogCategory.objects.create(name="tree category 1", app_config=self.app_config_1)
        category2 = BlogCategory.objects.create(name="tree category 2", parent=category1, app_config=self.app_config_1)
        category3 = BlogCategory.objects.create(name="tree category 3", parent=category2, app_config=self.app_config_1)
        BlogCategory.objects.create(name="tree category 4", parent=category3, app_config=self.app_config_1)
        BlogCategory.objects.create(name="category different branch", app_config=self.app_config_2)

        post_admin = admin.site._registry[BlogCategory]
        request = self.get_page_request("/", self.user, r"/en/blog/?app_config=%s" % self.app_config_1.pk, edit=False)

        # Add view shows all the exising categories
        response = post_admin.add_view(request)
        self.assertTrue(
            response.context_data["adminform"].form.fields["parent"].queryset,
            BlogCategory.objects.filter(app_config=self.app_config_1),
        )

        # Changeview hides the children of the current category
        response = post_admin.change_view(request, str(category2.pk))
        self.assertTrue(
            response.context_data["adminform"].form.fields["parent"].queryset,
            BlogCategory.objects.filter(app_config=self.app_config_1, parent__isnull=True),
        )

        # Test second apphook categories
        request = self.get_page_request("/", self.user, r"/en/blog/?app_config=%s" % self.app_config_2.pk, edit=False)
        response = post_admin.add_view(request)
        self.assertTrue(
            response.context_data["adminform"].form.fields["parent"].queryset,
            BlogCategory.objects.filter(app_config=self.app_config_2),
        )

    def test_admin_fieldsets(self):
        handler = BaseHandler()
        post_admin = admin.site._registry[Post]
        request = self.get_page_request(
            "/", self.user_staff, r"/en/blog/?app_config=%s" % self.app_config_1.pk, edit=False
        )

        # Use placeholder
        self.app_config_1.app_data.config.use_placeholder = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("post_text" in fsets[0][1]["fields"])

        self.app_config_1.app_data.config.use_placeholder = False
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue("post_text" in fsets[0][1]["fields"])

        self.app_config_1.app_data.config.use_placeholder = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("post_text" in fsets[0][1]["fields"])

        # Use related posts
        self.app_config_1.app_data.config.use_related = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("related" in fsets[1][1]["fields"][0])

        Post.objects.language("en").create(title="post x", app_config=self.app_config_1)
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue("related" in fsets[1][1]["fields"][0])

        self.app_config_1.app_data.config.use_related = False
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("related" in fsets[1][1]["fields"][0])

        self.app_config_1.app_data.config.use_related = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue("related" in fsets[1][1]["fields"][0])

        # Use abstract
        self.app_config_1.app_data.config.use_abstract = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue("abstract" in fsets[0][1]["fields"])

        self.app_config_1.app_data.config.use_abstract = False
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("abstract" in fsets[0][1]["fields"])

        self.app_config_1.app_data.config.use_abstract = True
        self.app_config_1.app_data.config.default_image_full = self.default_full
        self.app_config_1.app_data.config.default_image_thumbnail = self.default_thumbnail
        self.app_config_1.save()

        with self.settings(BLOG_MULTISITE=True):
            fsets = post_admin.get_fieldsets(request)
            self.assertTrue("sites" in fsets[1][1]["fields"][0])
        with self.settings(BLOG_MULTISITE=False):
            fsets = post_admin.get_fieldsets(request)
            self.assertFalse("sites" in fsets[1][1]["fields"][0])

        request = self.get_page_request("/", self.user, r"/en/blog/?app_config=%s" % self.app_config_1.pk, edit=False)
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue("author" in fsets[1][1]["fields"][0])

        with self.login_user_context(self.user):
            request = self.get_request(
                "/", "en", user=self.user, path=r"/en/blog/?app_config=%s" % self.app_config_1.pk
            )
            msg_mid = MessageMiddleware(handler)
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            response = post_admin.add_view(request)
            self.assertTrue(
                response.context_data["adminform"].form.fields["categories"].queryset,
                BlogCategory.objects.filter(app_config=self.app_config_1),
            )
            response.render()
            self.assertContains(response, 'id="id_sites"')
            self.assertRegex(force_str(response.content), r"selected[^>]*>Blog image")
            self.assertRegex(force_str(response.content), r"selected[^>]*>Blog thumbnail")

            # Add view select categories on the given appconfig, even when reloading the form
            request.POST = QueryDict("app_config=%s" % self.app_config_1.pk)
            request.method = "POST"
            response = post_admin.add_view(request)
            self.assertTrue(
                response.context_data["adminform"].form.fields["categories"].queryset,
                BlogCategory.objects.filter(app_config=self.app_config_1),
            )

            request.GET = QueryDict("app_config=%s" % self.app_config_1.pk)
            request.method = "GET"
            response = post_admin.add_view(request)
            self.assertTrue(
                response.context_data["adminform"].form.fields["categories"].queryset,
                BlogCategory.objects.filter(app_config=self.app_config_1),
            )

        self.user.sites.add(self.site_1)
        with self.login_user_context(self.user):
            request = self.get_request(
                "/", "en", user=self.user, path=r"/en/blog/?app_config=%s" % self.app_config_1.pk
            )
            msg_mid = MessageMiddleware(handler)
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            post_admin._sites = None
            response = post_admin.add_view(request)
            response.render()
            self.assertNotContains(response, 'id="id_sites" name="sites"')
            post_admin._sites = None
        self.user.sites.clear()

    def test_custom_admin_fieldsets(self):
        post_admin = CustomPostAdmin(Post, admin_site=admin.site)
        request = self.get_page_request(
            "/", self.user_staff, r"/en/blog/?app_config=%s" % self.app_config_1.pk, edit=False
        )

        # Use placeholder
        self.app_config_1.app_data.config.use_placeholder = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("post_text" in fsets[0][1]["fields"])

        self.app_config_1.app_data.config.use_placeholder = False
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue("post_text" in fsets[0][1]["fields"])

        self.app_config_1.app_data.config.use_placeholder = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("post_text" in fsets[0][1]["fields"])

        # Related field is always hidden due to the value in CustomPostAdmin._fieldset_extra_fields_position
        self.app_config_1.app_data.config.use_related = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("related" in fsets[1][1]["fields"][0])

        Post.objects.language("en").create(title="post x", app_config=self.app_config_1)
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("related" in fsets[1][1]["fields"][0])

        self.app_config_1.app_data.config.use_related = False
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("related" in fsets[1][1]["fields"][0])

        self.app_config_1.app_data.config.use_related = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("related" in fsets[1][1]["fields"][0])

        # Use abstract
        self.app_config_1.app_data.config.use_abstract = True
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue("abstract" in fsets[0][1]["fields"])

        self.app_config_1.app_data.config.use_abstract = False
        self.app_config_1.save()
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("abstract" in fsets[0][1]["fields"])

        self.app_config_1.app_data.config.use_abstract = True
        self.app_config_1.app_data.config.default_image_full = self.default_full
        self.app_config_1.app_data.config.default_image_thumbnail = self.default_thumbnail
        self.app_config_1.save()

        with self.settings(BLOG_MULTISITE=True):
            fsets = post_admin.get_fieldsets(request)
            self.assertTrue("sites" in fsets[1][1]["fields"][0])
        with self.settings(BLOG_MULTISITE=False):
            fsets = post_admin.get_fieldsets(request)
            self.assertFalse("sites" in fsets[1][1]["fields"][0])

        request = self.get_page_request("/", self.user, r"/en/blog/?app_config=%s" % self.app_config_1.pk, edit=False)
        fsets = post_admin.get_fieldsets(request)
        self.assertTrue("author" in fsets[1][1]["fields"])

    def test_admin_queryset(self):
        posts = self.get_posts()
        posts[0].sites.add(self.site_1)
        posts[1].sites.add(self.site_2)

        request = self.get_request("/", "en", user=self.user, path=r"/en/blog/?app_config=%s" % self.app_config_1.pk)
        post_admin = admin.site._registry[Post]
        post_admin._sites = None
        qs = post_admin.get_queryset(request)
        self.assertEqual(qs.count(), 4)

        self.user.sites.add(self.site_2)
        request = self.get_request("/", "en", user=self.user, path=r"/en/blog/?app_config=%s" % self.app_config_1.pk)
        post_admin = admin.site._registry[Post]
        post_admin._sites = None
        qs = post_admin.get_queryset(request)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0], posts[1])
        self.user.sites.clear()

    def test_admin_auto_author(self):
        pages = self.get_pages()
        data = deepcopy(self._post_data[0]["en"])
        handler = BaseHandler()

        with self.login_user_context(self.user):
            self.app_config_1.app_data.config.set_author = True
            self.app_config_1.save()
            data["date_published_0"] = now().strftime("%Y-%m-%d")
            data["date_published_1"] = now().strftime("%H:%M:%S")
            data["categories"] = self.category_1.pk
            data["app_config"] = self.app_config_1.pk
            request = self.post_request(
                pages[0], "en", user=self.user, data=data, path=r"/en/blog/?app_config=%s" % self.app_config_1.pk
            )
            msg_mid = MessageMiddleware(handler)
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            response = post_admin.add_view(request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Post.objects.count(), 1)
            self.assertEqual(Post.objects.get(translations__slug="first-post").author_id, request.user.pk)

            self.app_config_1.app_data.config.set_author = False
            self.app_config_1.save()
            data = deepcopy(self._post_data[1]["en"])
            data["date_published_0"] = now().strftime("%Y-%m-%d")
            data["date_published_1"] = now().strftime("%H:%M:%S")
            data["categories"] = self.category_1.pk
            data["app_config"] = self.app_config_1.pk
            request = self.post_request(
                pages[0], "en", user=self.user, data=data, path=r"/en/blog/?app_config=%s" % self.app_config_1.pk
            )
            msg_mid = MessageMiddleware(handler)
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            response = post_admin.add_view(request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Post.objects.count(), 2)
            self.assertEqual(Post.objects.get(translations__slug="second-post").author_id, None)

            with self.settings(BLOG_AUTHOR_DEFAULT="staff"):
                self.app_config_1.app_data.config.set_author = True
                self.app_config_1.save()
                data = deepcopy(self._post_data[2]["en"])
                data["date_published_0"] = now().strftime("%Y-%m-%d")
                data["date_published_1"] = now().strftime("%H:%M:%S")
                data["categories"] = self.category_1.pk
                data["app_config"] = self.app_config_1.pk
                request = self.post_request(
                    pages[0], "en", user=self.user, data=data, path=r"/en/blog/?app_config=%s" % self.app_config_1.pk
                )
                msg_mid = MessageMiddleware(handler)
                msg_mid.process_request(request)
                post_admin = admin.site._registry[Post]
                response = post_admin.add_view(request)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(Post.objects.count(), 3)
                self.assertEqual(Post.objects.get(translations__slug="third-post").author.username, "staff")

    def test_admin_fieldsets_filter(self):
        post_admin = admin.site._registry[Post]
        request = self.get_page_request("/", self.user_normal, r"/en/blog/?app_config=%s" % self.app_config_1.pk)

        post_admin._sites = None
        fsets = post_admin.get_fieldsets(request)
        self.assertFalse("author" in fsets[1][1]["fields"][0])
        self.assertTrue("sites" in fsets[1][1]["fields"][0])
        post_admin._sites = None

        def filter_function(fs, request, obj=None):
            if request.user == self.user_normal:
                fs[1][1]["fields"][0].append("author")
            return fs

        self.user_normal.sites.add(self.site_1)
        request = self.get_page_request("/", self.user_normal, r"/en/blog/?app_config=%s" % self.app_config_1.pk)
        post_admin._sites = None
        with self.settings(BLOG_ADMIN_POST_FIELDSET_FILTER=filter_function):
            fsets = post_admin.get_fieldsets(request)
            self.assertTrue("author" in fsets[1][1]["fields"][0])
            self.assertFalse("sites" in fsets[1][1]["fields"][0])
        post_admin._sites = None
        self.user_normal.sites.clear()

    def test_admin_post_text(self):
        pages = self.get_pages()
        post = self._get_post(self._post_data[0]["en"])
        handler = BaseHandler()

        with pause_knocks(post):
            with self.login_user_context(self.user):
                with self.settings(BLOG_USE_PLACEHOLDER=False):
                    data = {"post_text": "ehi text", "title": "some title"}
                    request = self.post_request(
                        pages[0], "en", user=self.user, data=data, path="/en/?edit_fields=post_text"
                    )
                    msg_mid = MessageMiddleware(handler)
                    msg_mid.process_request(request)
                    post_admin = admin.site._registry[Post]
                    response = post_admin.edit_field(request, post.pk, "en")
                    self.assertEqual(response.status_code, 200)
                    modified_post = Post.objects.language("en").get(pk=post.pk)
                    self.assertEqual(modified_post.safe_translation_getter("post_text"), data["post_text"])

    def test_admin_publish_post_view(self):
        self.get_pages()
        post = self._get_post(self._post_data[0]["en"])

        with pause_knocks(post):
            post.publish = False
            post.save()
            self.client.force_login(self.user)
            response = self.client.post(reverse("admin:djangocms_blog_publish_article", args=(post.pk,)))
            post.refresh_from_db()
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response["Location"], post.get_absolute_url())
            self.assertTrue(post.publish)

    def test_admin_site(self):
        pages = self.get_pages()
        post = self._get_post(self._post_data[0]["en"])
        handler = BaseHandler()

        # no restrictions, sites are assigned
        with self.login_user_context(self.user):
            data = {
                "sites": [self.site_1.pk, self.site_2.pk],
                "title": "some title",
                "app_config": self.app_config_1.pk,
            }
            request = self.post_request(pages[0], "en", user=self.user, data=data, path="/en/")
            self.assertEqual(post.sites.count(), 0)
            msg_mid = MessageMiddleware(handler)
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            response = post_admin.change_view(request, str(post.pk))
            self.assertEqual(response.status_code, 302)
            post = self.reload_model(post)
            self.assertEqual(post.sites.count(), 2)
        post.sites.clear()
        post = self.reload_model(post)

        # user only allowed on 2 sites, can add both
        self.user.sites.add(self.site_2)
        self.user.sites.add(self.site_3)
        post.sites.add(self.site_1)
        post.sites.add(self.site_2)
        self.user = self.reload_model(self.user)
        with self.login_user_context(self.user):
            data = {
                "sites": [self.site_2.pk, self.site_3.pk],
                "title": "some title",
                "app_config": self.app_config_1.pk,
            }
            request = self.post_request(pages[0], "en", user=self.user, data=data, path="/en/")
            self.assertEqual(post.sites.count(), 2)
            msg_mid = MessageMiddleware(handler)
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            post_admin._sites = None
            response = post_admin.change_view(request, str(post.pk))
            self.assertEqual(response.status_code, 302)
            post = self.reload_model(post)
            self.assertEqual(post.sites.count(), 3)
        self.user.sites.clear()
        post.sites.clear()

        # user only allowed on 2 sites, can remove one of his sites
        post = self.reload_model(post)
        post.sites.add(self.site_1)
        post.sites.add(self.site_2)
        post.sites.add(self.site_3)
        self.user.sites.add(self.site_2)
        self.user.sites.add(self.site_3)
        with self.login_user_context(self.user):
            data = {"sites": [self.site_3.pk], "title": "some title", "app_config": self.app_config_1.pk}
            request = self.post_request(pages[0], "en", user=self.user, data=data, path="/en/")
            self.assertEqual(post.sites.count(), 3)
            msg_mid = MessageMiddleware(handler)
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            post_admin._sites = None
            response = post_admin.change_view(request, str(post.pk))
            self.assertEqual(response.status_code, 302)
            post = self.reload_model(post)
            self.assertEqual(post.sites.count(), 2)
        self.user.sites.clear()
        post.sites.clear()

        # user only allowed on 2 sites, if given sites is empty, the site with no permission on
        # is kept
        post = self.reload_model(post)
        post.sites.add(self.site_1)
        post.sites.add(self.site_3)
        self.user.sites.add(self.site_2)
        self.user.sites.add(self.site_3)
        with self.login_user_context(self.user):
            data = {"sites": [], "title": "some title", "app_config": self.app_config_1.pk}
            request = self.post_request(pages[0], "en", user=self.user, data=data, path="/en/")
            self.assertEqual(post.sites.count(), 2)
            msg_mid = MessageMiddleware(handler)
            msg_mid.process_request(request)
            post_admin = admin.site._registry[Post]
            post_admin._sites = None
            response = post_admin.change_view(request, str(post.pk))
            self.assertEqual(response.status_code, 302)
            post = self.reload_model(post)
            self.assertEqual(post.sites.count(), 1)
        self.user.sites.clear()
        post.sites.clear()
        self.reload_model(post)

    def test_admin_clear_menu(self):
        """
        Tests that after changing apphook config menu structure the menu content is different: new
        value is taken immediately into account
        """
        handler = BaseHandler()
        self._reload_menus()

        pages = self.get_pages()
        post = self._get_post(self._post_data[0]["en"])

        request = self.get_page_request(None, self.user, r"/en/page-two/")
        first_nodes = self.get_nodes(menu_pool, request)
        self._reset_menus()
        with pause_knocks(post):
            with self.login_user_context(self.user):
                data = dict(namespace="sample_app", app_title="app1", object_name="Blog")
                data["config-menu_structure"] = MENU_TYPE_NONE
                data["config-sitemap_changefreq"] = "weekly"
                data["config-sitemap_priority"] = "0.5"
                request = self.post_request(pages[0], "en", user=self.user, data=data)
                msg_mid = MessageMiddleware(handler)
                msg_mid.process_request(request)
                config_admin = admin.site._registry[BlogConfig]
                config_admin.change_view(request, str(self.app_config_1.pk))
                second_nodes = self.get_nodes(menu_pool, request)
                self.assertNotEqual(len(first_nodes), len(second_nodes))


class ModelsTest(BaseTest):
    def test_category_attributes(self):
        posts = self.get_posts()
        posts[0].publish = True
        posts[0].save()
        posts[1].publish = True
        posts[1].save()
        posts[1].sites.add(self.site_2)
        new_category = BlogCategory.objects.create(name="category 2", app_config=self.app_config_1)
        posts[1].categories.add(new_category)

        with self.settings(SITE_ID=2):
            self.assertEqual(new_category.count, 1)
            self.assertEqual(self.category_1.count, 2)
            self.assertEqual(new_category.count_all_sites, 1)
            self.assertEqual(self.category_1.count_all_sites, 2)

        # needed to clear cached properties
        new_category = self.reload_model(new_category)
        self.category_1 = self.reload_model(self.category_1)
        with self.settings(SITE_ID=1):
            self.assertEqual(new_category.count, 0)
            self.assertEqual(self.category_1.count, 1)
            self.assertEqual(new_category.count_all_sites, 1)
            self.assertEqual(self.category_1.count_all_sites, 2)

    def test_slug(self):
        post = Post.objects.language("en").create(title="I am a title")
        self.assertEqual(post.slug, "i-am-a-title")

        # Test unicode chars in slugs
        post = Post.objects.language("fr").create(title="Accentué")
        self.assertEqual(post.slug, "accentué")

    def test_model_attributes(self):
        self.get_pages()

        featured_date = now() + timedelta(days=40)

        post = self._get_post(self._post_data[0]["en"])
        post = self._get_post(self._post_data[0]["it"], post, "it")
        post.main_image = self.create_filer_image_object()
        post.publish = True
        post.save()
        post.set_current_language("en")
        self.assertEqual(post.date, post.date_published)

        post.date_featured = featured_date
        post.save()
        self.assertEqual(post.date, featured_date)

        meta_en = post.as_meta()
        self.assertEqual(meta_en.og_type, get_setting("FB_TYPE"))
        self.assertEqual(meta_en.title, post.title)
        self.assertTrue(meta_en.url.endswith(post.get_absolute_url()))
        self.assertEqual(meta_en.description, post.meta_description)
        self.assertEqual(meta_en.keywords, post.meta_keywords.split(","))
        self.assertEqual(meta_en.published_time, post.date_published)
        self.assertEqual(meta_en.locale, "en")
        self.assertEqual(meta_en.twitter_site, "")
        self.assertEqual(meta_en.twitter_author, "")
        self.assertEqual(meta_en.twitter_type, "summary")
        self.assertEqual(meta_en.schemaorg_type, "Blog")
        self.assertEqual(meta_en.schemaorg_title, post.title)
        self.assertEqual(meta_en.schemaorg_description, post.meta_description)
        self.assertEqual(meta_en.og_type, "Article")
        self.assertEqual(meta_en.image_width, post.main_image.width)
        self.assertEqual(meta_en.image_height, post.main_image.height)
        self.assertEqual(meta_en.facebook_app_id, None)
        post.set_current_language("it")
        meta_it = post.as_meta()
        self.assertEqual(meta_it.title, post.title)
        self.assertTrue(meta_it.url.endswith(post.get_absolute_url()))
        self.assertNotEqual(meta_it.title, meta_en.title)
        self.assertEqual(meta_it.description, post.meta_description)

        category = post.categories.first()
        meta_cat = category.as_meta()
        self.assertEqual(meta_cat.og_type, get_setting("FB_TYPE"))
        self.assertEqual(meta_cat.title, category.name)
        self.assertEqual(meta_cat.description, category.meta_description)
        self.assertEqual(meta_cat.locale, "en")
        self.assertEqual(meta_cat.twitter_site, "")
        self.assertEqual(meta_cat.twitter_author, "")
        self.assertEqual(meta_cat.twitter_type, "summary")
        self.assertEqual(meta_cat.schemaorg_type, "Blog")
        self.assertEqual(meta_cat.og_type, "Article")
        self.assertEqual(meta_cat.facebook_app_id, None)
        self.assertTrue(meta_cat.url.endswith(category.get_absolute_url()))

        with override("en"):
            post.set_current_language(get_language())
            kwargs = {
                "year": post.date_published.year,
                "month": "%02d" % post.date_published.month,
                "day": "%02d" % post.date_published.day,
                "slug": post.safe_translation_getter("slug", any_language=get_language()),
            }
            url_en = reverse(
                "%s:post-detail" % self.app_config_1.namespace, kwargs=kwargs, current_app=self.app_config_1.namespace
            )
            self.assertEqual(url_en, post.get_absolute_url())

        with override("it"):
            post.set_current_language(get_language())
            kwargs = {
                "year": post.date_published.year,
                "month": "%02d" % post.date_published.month,
                "day": "%02d" % post.date_published.day,
                "slug": post.safe_translation_getter("slug", any_language=get_language()),
            }
            url_it = reverse(
                "%s:post-detail" % self.app_config_1.namespace, kwargs=kwargs, current_app=self.app_config_1.namespace
            )
            self.assertEqual(url_it, post.get_absolute_url())
            self.assertNotEqual(url_it, url_en)

            self.assertEqual(post.get_full_url(), "http://example.com%s" % url_it)
        self.assertEqual(post.get_image_full_url(), "http://example.com%s" % post.main_image.url)

        self.assertEqual(post.thumbnail_options(), get_setting("IMAGE_THUMBNAIL_SIZE"))
        self.assertEqual(post.full_image_options(), get_setting("IMAGE_FULL_SIZE"))

        post.main_image_thumbnail = self.thumb_1
        post.main_image_full = self.thumb_2
        self.assertEqual(
            post.thumbnail_options(), {"size": (100, 100), "width": 100, "height": 100, "crop": True, "upscale": False}
        )
        self.assertEqual(
            post.full_image_options(),
            {"size": (200, 200), "width": 200, "height": 200, "crop": False, "upscale": False},
        )

        post.set_current_language("en")
        post.meta_title = "meta title"
        self.assertEqual(post.get_title(), "meta title")

        # Assess is_published property
        post.publish = False
        post.save()
        self.assertFalse(post.is_published)

        post.publish = True
        post.date_published = now() + timedelta(days=1)
        post.date_published_end = None
        post.save()
        self.assertFalse(post.is_published)

        post.publish = True
        post.date_published = now() - timedelta(days=1)
        post.date_published_end = now() - timedelta(minutes=1)
        post.save()
        self.assertFalse(post.is_published)

        post.publish = True
        post.date_published = now() - timedelta(days=1)
        post.date_published_end = None
        post.save()
        self.assertTrue(post.is_published)

        post.publish = True
        post.date_published = now() - timedelta(days=1)
        post.date_published_end = now() + timedelta(minutes=1)
        post.save()
        self.assertTrue(post.is_published)

        post.publish = False
        post.date_published = now() - timedelta(days=1)
        post.date_published_end = None
        post.save()
        self.assertFalse(post.is_published)

        post.publish = False
        post.date_published = now() - timedelta(days=1)
        post.date_published_end = now() + timedelta(minutes=1)
        post.save()
        self.assertFalse(post.is_published)

    def test_model_meta_image_setting(self):
        post = self._get_post(self._post_data[0]["en"])
        post.main_image = self.create_filer_image_object()
        post.save()

        post.set_current_language("en")
        meta_en = post.as_meta()
        self.assertEqual(meta_en.image, post.build_absolute_uri(post.main_image.url))
        self.assertEqual(meta_en.image_width, post.main_image.width)
        self.assertEqual(meta_en.image_height, post.main_image.height)

        with override_settings(BLOG_META_IMAGE_SIZE={"size": (1200, 630), "crop": True, "upscale": False}):
            meta_en = post.as_meta()
            self.assertEqual(
                meta_en.image,
                post.build_absolute_uri(
                    get_thumbnailer(post.main_image).get_thumbnail(get_setting("META_IMAGE_SIZE")).url
                ),
            )
            self.assertEqual(
                meta_en.image_width,
                get_thumbnailer(post.main_image).get_thumbnail(get_setting("META_IMAGE_SIZE")).width,
            )
            self.assertEqual(
                meta_en.image_height,
                get_thumbnailer(post.main_image).get_thumbnail(get_setting("META_IMAGE_SIZE")).height,
            )

    def test_urls(self):
        self.get_pages()
        post = self._get_post(self._post_data[0]["en"])
        post = self._get_post(self._post_data[0]["it"], post, "it")

        # default
        self.assertTrue(re.match(r".*\d{4}/\d{2}/\d{2}/%s/$" % post.slug, post.get_absolute_url()))

        # full date
        self.app_config_1.app_data.config.url_patterns = "full_date"
        self.app_config_1.save()
        post.app_config = self.app_config_1
        self.assertTrue(re.match(r".*\d{4}/\d{2}/\d{2}/%s/$" % post.slug, post.get_absolute_url()))

        # short date
        self.app_config_1.app_data.config.url_patterns = "short_date"
        self.app_config_1.save()
        post.app_config = self.app_config_1
        self.assertTrue(re.match(r".*\d{4}/\d{2}/%s/$" % post.slug, post.get_absolute_url()))

        # category
        self.app_config_1.app_data.config.url_patterns = "category"
        self.app_config_1.save()
        post.app_config = self.app_config_1
        self.assertTrue(re.match(r".*/\w[-\w]*/%s/$" % post.slug, post.get_absolute_url()))
        self.assertTrue(
            re.match(r".*{}/{}/$".format(post.categories.first().slug, post.slug), post.get_absolute_url())
        )

        # slug only
        self.app_config_1.app_data.config.url_patterns = "category"
        self.app_config_1.save()
        post.app_config = self.app_config_1
        self.assertTrue(re.match(r".*/%s/$" % post.slug, post.get_absolute_url()))

        # Unicode chars in slugs
        post = Post.objects.language("fr").create(title="Accentué")
        category = BlogCategory.objects.create(name="Catégorie 2", app_config=self.app_config_1)
        category.set_current_language("fr", initialize=True)
        post.categories.add(category)

        # full date
        self.app_config_1.app_data.config.url_patterns = "full_date"
        self.app_config_1.save()
        post.app_config = self.app_config_1
        self.assertTrue(re.match(r".*\d{4}/\d{2}/\d{2}/%s/$" % quote(post.slug), post.get_absolute_url()))

        # short date
        self.app_config_1.app_data.config.url_patterns = "short_date"
        self.app_config_1.save()
        post.app_config = self.app_config_1
        self.assertTrue(re.match(r".*\d{4}/\d{2}/%s/$" % quote(post.slug), post.get_absolute_url()))

        # category
        self.app_config_1.app_data.config.url_patterns = "category"
        self.app_config_1.save()
        post.app_config = self.app_config_1

        self.assertTrue(
            re.match(
                r".*{}/{}/$".format(quote(post.categories.first().slug), quote(post.slug)),
                post.get_absolute_url(),
            )
        )

        # slug only
        self.app_config_1.app_data.config.url_patterns = "category"
        self.app_config_1.save()
        post.app_config = self.app_config_1
        self.assertTrue(re.match(r".*/%s/$" % quote(post.slug), post.get_absolute_url()))

    def test_url_language(self):
        self.get_pages()
        post = self._get_post(self._post_data[0]["en"])
        post = self._get_post(self._post_data[0]["it"], post, "it")

        with override("it"):
            self.assertEqual(post.get_current_language(), "en")
            self.assertEqual(post.get_absolute_url(), post.get_absolute_url("it"))

        post.set_current_language("it")
        with override("en"):
            self.assertEqual(post.get_current_language(), "it")
            self.assertEqual(post.get_absolute_url(), post.get_absolute_url("en"))

    def test_url_language_use_fallback(self):
        self.get_pages()
        post = self._get_post(self._post_data[0]["en"])

        PARLER_FALLBACK = {  # noqa: N806
            1: (
                {"code": "en"},
                {"code": "it"},
            ),
            "default": {"fallbacks": ["fr", "en"], "hide_untranslated": False},
        }
        PARLER_FALLBACK = add_default_language_settings(PARLER_FALLBACK)  # noqa: N806

        with override_parler_settings(PARLER_LANGUAGES=PARLER_FALLBACK):
            with override("it"):
                post.set_current_language("it")
                self.assertEqual(post.get_absolute_url(), post.get_absolute_url("it"))

            with override_settings(BLOG_USE_FALLBACK_LANGUAGE_IN_URL=True):
                with override("it"):
                    post.set_current_language("it")
                    self.assertEqual(post.get_absolute_url(), post.get_absolute_url("en"))

    def test_manager(self):
        self.get_pages()
        post1 = self._get_post(self._post_data[0]["en"])
        post2 = self._get_post(self._post_data[1]["en"])

        # default queryset, published and unpublished posts
        months = Post.objects.get_months()
        for data in months:
            self.assertEqual(data["date"].date(), now().replace(year=now().year, month=now().month, day=1).date())
            self.assertEqual(data["count"], 2)

        # custom queryset, only published
        post1.publish = True
        post1.save()
        months = Post.objects.get_months(Post.objects.published())
        for data in months:
            self.assertEqual(data["date"].date(), now().replace(year=now().year, month=now().month, day=1).date())
            self.assertEqual(data["count"], 1)

        # Move post to different site to filter it out
        post2.sites.add(self.site_2)
        months = Post.objects.get_months()
        for data in months:
            self.assertEqual(data["date"].date(), now().replace(year=now().year, month=now().month, day=1).date())
            self.assertEqual(data["count"], 1)
        months = Post.objects.get_months(current_site=False)
        for data in months:
            self.assertEqual(data["date"].date(), now().replace(year=now().year, month=now().month, day=1).date())
            self.assertEqual(data["count"], 2)
        post2.sites.clear()

        self.assertEqual(len(Post.objects.available()), 1)

        # If post is published but publishing date is in the future
        post2.date_published = now().replace(year=now().year + 1, month=now().month, day=1)
        post2.publish = True
        post2.save()
        self.assertEqual(len(Post.objects.available()), 2)
        self.assertEqual(len(Post.objects.published()), 1)
        self.assertEqual(len(Post.objects.published_future()), 2)
        self.assertEqual(len(Post.objects.archived()), 0)
        self.assertEqual(len(Post.objects.archived(current_site=False)), 0)

        # If post is published but end publishing date is in the past
        post2.date_published = now().replace(year=now().year - 2, month=now().month, day=1)
        post2.date_published_end = now().replace(year=now().year - 1, month=now().month, day=1)
        post2.save()
        self.assertEqual(len(Post.objects.available()), 2)
        self.assertEqual(len(Post.objects.published()), 1)
        self.assertEqual(len(Post.objects.archived()), 1)
        self.assertEqual(len(Post.objects.archived(current_site=False)), 1)

        # Move post to different site to filter it out
        post2.sites.add(self.site_2)
        self.assertEqual(len(Post.objects.archived()), 0)
        self.assertEqual(len(Post.objects.archived(current_site=False)), 1)
        self.assertEqual(len(Post.objects.available()), 1)
        self.assertEqual(len(Post.objects.available(current_site=False)), 2)
        self.assertEqual(len(Post.objects.published()), 1)

        # publish post
        post2.date_published = now() - timedelta(days=1)
        post2.date_published_end = now() + timedelta(days=10)
        post2.save()
        self.assertEqual(len(Post.objects.archived()), 0)
        self.assertEqual(len(Post.objects.archived(current_site=False)), 0)
        self.assertEqual(len(Post.objects.available()), 1)
        self.assertEqual(len(Post.objects.available(current_site=False)), 2)
        self.assertEqual(len(Post.objects.published()), 1)
        self.assertEqual(len(Post.objects.published(current_site=False)), 2)

        # counting with language fallback enabled
        self._get_post(self._post_data[0]["it"], post1, "it")
        self.assertEqual(len(Post.objects.filter_by_language("it")), 1)
        self.assertEqual(len(Post.objects.filter_by_language("it", current_site=False)), 2)
        post2.sites.clear()

        # No fallback
        parler.appsettings.PARLER_LANGUAGES["default"]["hide_untranslated"] = True
        for index, _lang in enumerate(parler.appsettings.PARLER_LANGUAGES[Site.objects.get_current().pk]):
            parler.appsettings.PARLER_LANGUAGES[Site.objects.get_current().pk][index]["hide_untranslated"] = True
        self.assertEqual(len(Post.objects.filter_by_language("it")), 1)
        parler.appsettings.PARLER_LANGUAGES["default"]["hide_untranslated"] = False
        for index, _lang in enumerate(parler.appsettings.PARLER_LANGUAGES[Site.objects.get_current().pk]):
            parler.appsettings.PARLER_LANGUAGES[Site.objects.get_current().pk][index]["hide_untranslated"] = False

    def test_tag_cloud(self):
        post1 = self._get_post(self._post_data[0]["en"])
        post2 = self._get_post(self._post_data[1]["en"])
        post1.tags.add("tag 1", "tag 2", "tag 3", "tag 4")
        post1.save()
        post2.tags.add("tag 6", "tag 2", "tag 5", "tag 8")
        post2.save()

        self.assertEqual(len(Post.objects.tag_cloud()), 0)

        tags = []
        for tag in Tag.objects.all():
            if tag.slug == "tag-2":
                tag.count = 2
            else:
                tag.count = 1
            tags.append(tag)

        self.assertEqual(Post.objects.tag_cloud(published=True), [])
        self.assertEqual(set(Post.objects.tag_cloud(published=False)), set(tags))

        tags_1 = []
        for tag in Tag.objects.all():
            if tag.slug == "tag-2":
                tag.count = 2
                tags_1.append(tag)
            elif tag.slug in ("tag-1", "tag-3", "tag-4"):
                tag.count = 1
                tags_1.append(tag)

        post1.publish = True
        post1.save()
        self.assertEqual(set(Post.objects.tag_cloud()), set(tags_1))
        self.assertEqual(set(Post.objects.tag_cloud(published=False)), set(tags))

        tags1 = set(Post.objects.tag_list(Post))
        tags2 = set(Tag.objects.all())
        self.assertEqual(tags1, tags2)

        self.assertEqual(
            list(Post.objects.tagged(queryset=Post.objects.filter(pk=post1.pk)).order_by("pk").values_list("pk")),
            list(Post.objects.filter(pk__in=(post1.pk, post2.pk)).order_by("pk").values_list("pk")),
        )

    def test_plugin_latest(self):
        post1 = self._get_post(self._post_data[0]["en"])
        self._get_post(self._post_data[1]["en"])
        post1.tags.add("tag 1")
        post1.save()
        request = self.get_page_request("/", AnonymousUser(), r"/en/blog/", edit=False)
        request_auth = self.get_page_request("/", self.user_staff, r"/en/blog/", edit=False)
        request_edit = self.get_page_request("/", self.user_staff, r"/en/blog/", edit=True)
        plugin = add_plugin(post1.content, "BlogLatestEntriesPlugin", language="en", app_config=self.app_config_1)
        tag = Tag.objects.get(slug="tag-1")
        plugin.tags.add(tag)
        # unauthenticated users get no post
        self.assertEqual(len(plugin.get_posts(request)), 0)
        # staff users not in edit mode get no post
        self.assertEqual(len(plugin.get_posts(request_auth)), 0)
        # staff users in edit mode get the post
        self.assertEqual(len(plugin.get_posts(request_edit, published_only=False)), 1)

        post1.publish = True
        post1.save()
        self.assertEqual(len(plugin.get_posts(request)), 1)


class ModelsTest2(BaseTest):
    def test_copy_plugin_latest(self):
        post1 = self._get_post(self._post_data[0]["en"])
        post2 = self._get_post(self._post_data[1]["en"])
        tag1 = Tag.objects.create(name="tag 1")
        tag2 = Tag.objects.create(name="tag 2")
        plugin = add_plugin(post1.content, "BlogLatestEntriesPlugin", language="en", app_config=self.app_config_1)
        plugin.tags.add(tag1)
        plugin.tags.add(tag2)
        plugins = list(post1.content.cmsplugin_set.filter(language="en").order_by("path", "depth", "position"))
        copy_plugins_to(plugins, post2.content)
        new = list(downcast_plugins(post2.content.cmsplugin_set.all()))
        self.assertEqual(set(new[0].tags.all()), {tag1, tag2})
        self.assertEqual(set(new[0].tags.all()), set(plugin.tags.all()))

    def test_plugin_author(self):
        post1 = self._get_post(self._post_data[0]["en"])
        post2 = self._get_post(self._post_data[1]["en"])
        request = self.get_page_request("/", AnonymousUser(), r"/en/blog/", edit=False)
        plugin = add_plugin(post1.content, "BlogAuthorPostsPlugin", language="en", app_config=self.app_config_1)
        plugin.authors.add(self.user)
        self.assertEqual(len(plugin.get_posts(request)), 0)
        self.assertEqual(plugin.get_authors(request)[0].count, 0)

        post1.publish = True
        post1.save()
        self.assertEqual(len(plugin.get_posts(request)), 1)
        self.assertEqual(plugin.get_authors(request)[0].count, 1)

        post2.publish = True
        post2.save()
        self.assertEqual(len(plugin.get_posts(request)), 2)
        self.assertEqual(plugin.get_authors(request)[0].count, 2)

    def test_plugin_featured_posts(self):
        post1 = self._get_post(self._post_data[0]["en"])
        post1.publish = True
        post1.save()
        post2 = self._get_post(self._post_data[1]["en"])
        request = self.get_page_request("/", AnonymousUser(), r"/en/blog/", edit=False)
        plugin = add_plugin(post1.content, "BlogFeaturedPostsPlugin", language="en", app_config=self.app_config_1)
        plugin.posts.add(post1, post2)
        self.assertEqual(len(plugin.get_posts(request)), 1)

        post2.publish = True
        post2.save()
        self.assertEqual(len(plugin.get_posts(request)), 2)

    def test_copy_plugin_featured_post(self):
        post1 = self._get_post(self._post_data[0]["en"])
        post2 = self._get_post(self._post_data[1]["en"])
        plugin = add_plugin(post1.content, "BlogFeaturedPostsPlugin", language="en", app_config=self.app_config_1)
        plugin.posts.add(post1, post2)
        plugins = list(post1.content.cmsplugin_set.filter(language="en").order_by("path", "depth", "position"))
        copy_plugins_to(plugins, post2.content)
        new = list(downcast_plugins(post2.content.cmsplugin_set.all()))
        self.assertEqual(set(new[0].posts.all()), {post1, post2})

    def test_copy_plugin_author(self):
        post1 = self._get_post(self._post_data[0]["en"])
        post2 = self._get_post(self._post_data[1]["en"])
        plugin = add_plugin(post1.content, "BlogAuthorPostsPlugin", language="en", app_config=self.app_config_1)
        plugin.authors.add(self.user)
        plugins = list(post1.content.cmsplugin_set.filter(language="en").order_by("path", "depth", "position"))
        copy_plugins_to(plugins, post2.content)
        new = list(downcast_plugins(post2.content.cmsplugin_set.all()))
        self.assertEqual(set(new[0].authors.all()), {self.user})

    def test_multisite(self):
        with override("en"):
            post1 = self._get_post(self._post_data[0]["en"], sites=(self.site_1,))
            post2 = self._get_post(self._post_data[1]["en"], sites=(self.site_2,))
            post3 = self._get_post(self._post_data[2]["en"], sites=(self.site_2, self.site_1))

            self.assertEqual(len(Post.objects.all()), 3)
            with self.settings(**{"SITE_ID": self.site_1.pk}):
                self.assertEqual(len(Post.objects.all().on_site()), 2)
                self.assertEqual(set(Post.objects.all().on_site()), {post1, post3})
            with self.settings(**{"SITE_ID": self.site_2.pk}):
                self.assertEqual(len(Post.objects.all().on_site()), 2)
                self.assertEqual(set(Post.objects.all().on_site()), {post2, post3})

    def test_str_repr(self):
        self.get_pages()
        post1 = self._get_post(self._post_data[0]["en"])
        post1.meta_description = ""
        post1.main_image = None
        post1.save()

        self.assertEqual(force_str(post1), post1.title)
        self.assertEqual(post1.get_description(), strip_tags(post1.abstract))
        self.assertEqual(post1.get_image_full_url(), "")
        self.assertEqual(post1.get_author(), self.user)

        self.assertEqual(force_str(post1.categories.first()), "category 1")

        plugin = add_plugin(post1.content, "BlogAuthorPostsPlugin", language="en", app_config=self.app_config_1)
        self.assertEqual(force_str(plugin.__str__()), "5 latest articles by author")

        plugin = add_plugin(post1.content, "BlogLatestEntriesPlugin", language="en", app_config=self.app_config_1)
        self.assertEqual(force_str(plugin.__str__()), "5 latest articles by tag")

        plugin = add_plugin(post1.content, "BlogArchivePlugin", language="en", app_config=self.app_config_1)
        self.assertEqual(force_str(plugin.__str__()), "generic blog plugin")

        plugin = add_plugin(post1.content, "BlogFeaturedPostsPlugin", language="en", app_config=self.app_config_1)
        self.assertEqual(plugin.__str__(), "Featured posts")

        # create fake empty post - assign a random pk to trick ORM / parler to think the object has been saved
        # due to how safe_translation_getter works
        no_translation_post = Post()
        no_translation_post.pk = 1000000
        no_translation_default_title = "Post (no translation)"
        self.assertEqual(force_str(no_translation_post), no_translation_default_title)


class KnockerTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        try:
            import knocker  # noqa

            super().setUpClass()
        except ImportError:
            raise SkipTest("django-knocker not installed, skipping tests")

    def test_model_attributes(self):
        self.get_pages()
        posts = self.get_posts()

        for language in posts[0].get_available_languages():
            with smart_override(language):
                posts[0].set_current_language(language)
                knock_create = posts[0].as_knock(signal_type="post_save", created=True)
                self.assertEqual(knock_create["title"], "new {}".format(posts[0]._meta.verbose_name))
                self.assertEqual(knock_create["message"], posts[0].title)
                self.assertEqual(knock_create["language"], language)

        for language in posts[0].get_available_languages():
            with smart_override(language):
                posts[0].set_current_language(language)
                knock_create = posts[0].as_knock(signal_type="post_save", created=False)
                self.assertEqual(knock_create["title"], "new {}".format(posts[0]._meta.verbose_name))
                self.assertEqual(knock_create["message"], posts[0].title)
                self.assertEqual(knock_create["language"], language)

    def test_should_knock(self):
        self.get_pages()

        post_data = {
            "author": self.user,
            "title": "post 1",
            "abstract": "post 1",
            "meta_description": "post 1",
            "meta_keywords": "post 1",
            "app_config": self.app_config_1,
        }
        post = Post.objects.create(**post_data)
        # Object is not published, no knock
        self.assertFalse(post.should_knock(signal_type="post_save"))
        post.publish = True
        post.save()
        # Object is published, send knock
        self.assertTrue(post.should_knock(signal_type="post_save"))

        # Knock disabled for updates
        self.app_config_1.app_data.config.send_knock_update = False
        self.app_config_1.save()
        post.abstract = "what"
        post.save()
        self.assertFalse(post.should_knock(signal_type="post_save"))

        # Knock disabled for publishing
        self.app_config_1.app_data.config.send_knock_create = False
        self.app_config_1.save()
        post_data = {
            "author": self.user,
            "title": "post 2",
            "abstract": "post 2",
            "meta_description": "post 2",
            "meta_keywords": "post 2",
            "app_config": self.app_config_1,
        }
        post = Post.objects.create(**post_data)
        self.assertFalse(post.should_knock(signal_type="post_save"))
        post.publish = True
        post.save()
        self.assertFalse(post.should_knock(signal_type="post_save"))

        # Restore default values
        self.app_config_1.app_data.config.send_knock_create = True
        self.app_config_1.app_data.config.send_knock_update = True
        self.app_config_1.save()
