import os.path
import re

from cms.api import add_plugin
from cms.models import Page
from cms.test_utils.util.fuzzy_int import FuzzyInt
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.timezone import now
from taggit.models import Tag

from djangocms_blog.models import BlogCategory

from .base import BaseTest

User = get_user_model()


class PluginTest(BaseTest):
    def test_plugin_latest_cached(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].tags.add("tag 1")
        posts[0].publish = True
        posts[0].save()
        ph = pages[0].placeholders.get(slot="content")

        plugin = add_plugin(ph, "BlogLatestEntriesPluginCached", language="en", app_config=self.app_config_1)
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        try:
            self.assertTrue(rendered.find("cms-plugin-djangocms_blog-post-abstract-%s" % posts[0].pk) > -1)
        except AssertionError:
            self.assertTrue(rendered.find("cms_plugin-djangocms_blog-post-abstract-%s" % posts[0].pk) > -1)
        self.assertTrue(rendered.find("<p>first line</p>") > -1)
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find(posts[0].get_absolute_url()) > -1)

        plugin_nocache = add_plugin(ph, "BlogLatestEntriesPlugin", language="en", app_config=self.app_config_1)
        # FIXME: Investigate the correct number of queries expected here
        with self.assertNumQueries(FuzzyInt(17, 18)):
            self.render_plugin(pages[0], "en", plugin_nocache)

        with self.assertNumQueries(FuzzyInt(17, 18)):
            self.render_plugin(pages[0], "en", plugin)

        with self.assertNumQueries(FuzzyInt(17, 18)):
            rendered = self.render_plugin(pages[0], "en", plugin)

        self.assertTrue(rendered.find("<p>first line</p>") > -1)
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find(posts[0].get_absolute_url()) > -1)

    def test_plugin_latest(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].tags.add("tag 1")
        posts[0].publish = True
        posts[0].save()
        ph = pages[0].placeholders.get(slot="content")

        plugin = add_plugin(ph, "BlogLatestEntriesPlugin", language="en", app_config=self.app_config_1)
        tag = Tag.objects.get(slug="tag-1")
        plugin.tags.add(tag)

        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        try:
            self.assertTrue(rendered.find("cms-plugin-djangocms_blog-post-abstract-%s" % posts[0].pk) > -1)
        except AssertionError:
            self.assertTrue(rendered.find("cms_plugin-djangocms_blog-post-abstract-%s" % posts[0].pk) > -1)
        self.assertTrue(rendered.find(reverse("sample_app:posts-tagged", kwargs={"tag": tag.slug})) > -1)
        self.assertTrue(rendered.find("<p>first line</p>") > -1)
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find(posts[0].get_absolute_url()) > -1)

        category_2 = BlogCategory.objects.create(name="category 2", app_config=self.app_config_1)
        category_2.set_current_language("it", initialize=True)
        category_2.name = "categoria 2"
        category_2.save()
        category_2.set_current_language("en")
        posts[1].categories.add(category_2)
        plugin = add_plugin(ph, "BlogLatestEntriesPlugin", language="en", app_config=self.app_config_1)
        plugin.categories.add(category_2)

        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        try:
            self.assertTrue(rendered.find("cms-plugin-djangocms_blog-post-abstract-%s" % posts[1].pk) > -1)
        except AssertionError:
            self.assertTrue(rendered.find("cms_plugin-djangocms_blog-post-abstract-%s" % posts[1].pk) > -1)
        self.assertTrue(rendered.find(reverse("sample_app:posts-category", kwargs={"category": category_2.slug})) > -1)
        self.assertTrue(rendered.find("<p>second post first line</p>") > -1)
        self.assertTrue(rendered.find('<article id="post-second-post"') > -1)
        self.assertTrue(rendered.find(posts[1].get_absolute_url()) > -1)

        # Checking copy relations
        ph = pages[0].placeholders.get(slot="content")
        original = ph.get_plugins("en")
        pages[0].publish("en")
        published = pages[0].get_public_object()
        ph = published.placeholders.get(slot="content")
        new = ph.get_plugins("en")
        self.assertNotEqual(original, new)

        casted_tags, __ = new[0].get_plugin_instance()
        casted_categories, __ = new[1].get_plugin_instance()

        self.assertEqual(casted_tags.tags.count(), 1)
        self.assertEqual(casted_tags.categories.count(), 0)

        self.assertEqual(casted_categories.tags.count(), 0)
        self.assertEqual(casted_categories.categories.count(), 1)

        posts[1].sites.add(self.site_2)
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertFalse(rendered.find("<p>second post first line</p>") > -1)

        posts[1].sites.remove(self.site_2)
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertTrue(rendered.find("<p>second post first line</p>") > -1)

        plugin = add_plugin(ph, "BlogLatestEntriesPlugin", language="en")
        rendered = self.render_plugin(pages[0], "en", plugin, edit=False)
        # data is picked from both apphook configs
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find('<article id="post-different-appconfig"') > -1)

    def test_plugin_featured_cached(self):
        pages = self.get_pages()
        posts = self.get_posts()
        ph = pages[0].placeholders.get(slot="content")

        plugin = add_plugin(ph, "BlogFeaturedPostsPluginCached", language="en", app_config=self.app_config_1)
        plugin.posts.add(posts[0])
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        try:
            self.assertTrue(rendered.find("cms-plugin-djangocms_blog-post-abstract-%s" % posts[0].pk) > -1)
        except AssertionError:
            self.assertTrue(rendered.find("cms_plugin-djangocms_blog-post-abstract-%s" % posts[0].pk) > -1)
        self.assertTrue(rendered.find("<p>first line</p>") > -1)
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find(posts[0].get_absolute_url()) > -1)

        plugin_nocache = add_plugin(ph, "BlogFeaturedPostsPlugin", language="en", app_config=self.app_config_1)
        plugin_nocache.posts.add(posts[0])
        # FIXME: Investigate the correct number of queries expected here
        with self.assertNumQueries(FuzzyInt(14, 15)):
            self.render_plugin(pages[0], "en", plugin_nocache)

        with self.assertNumQueries(FuzzyInt(14, 15)):
            self.render_plugin(pages[0], "en", plugin)

        with self.assertNumQueries(FuzzyInt(14, 15)):
            rendered = self.render_plugin(pages[0], "en", plugin)

        self.assertTrue(rendered.find("<p>first line</p>") > -1)
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find(posts[0].get_absolute_url()) > -1)

    def test_plugin_featured(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[1].publish = True
        posts[1].save()
        ph = pages[0].placeholders.get(slot="content")

        plugin = add_plugin(ph, "BlogFeaturedPostsPlugin", language="en", app_config=self.app_config_1)
        plugin.posts.add(posts[0], posts[1])

        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        try:
            self.assertTrue(rendered.find("cms-plugin-djangocms_blog-post-abstract-%s" % posts[0].pk) > -1)
            self.assertTrue(rendered.find("cms-plugin-djangocms_blog-post-abstract-%s" % posts[1].pk) > -1)
        except AssertionError:
            self.assertTrue(rendered.find("cms_plugin-djangocms_blog-post-abstract-%s" % posts[0].pk) > -1)
            self.assertTrue(rendered.find("cms_plugin-djangocms_blog-post-abstract-%s" % posts[1].pk) > -1)
        self.assertTrue(rendered.find("<p>first line</p>") > -1)
        self.assertTrue(rendered.find("<p>second post first line</p>") > -1)
        self.assertTrue(rendered.find('<article id="post-first-post"') > -1)
        self.assertTrue(rendered.find('<article id="post-second-post"') > -1)
        self.assertTrue(rendered.find(posts[0].get_absolute_url()) > -1)
        self.assertTrue(rendered.find(posts[1].get_absolute_url()) > -1)

    def test_plugin_tags(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].tags.add("tag 1", "tag 2", "test tag")
        posts[0].publish = True
        posts[0].save()
        posts[1].tags.add("test tag", "another tag")
        posts[1].publish = True
        posts[1].save()
        ph = pages[0].placeholders.get(slot="content")
        plugin = add_plugin(ph, "BlogTagsPlugin", language="en", app_config=self.app_config_1)
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        for tag in Tag.objects.all():
            self.assertTrue(rendered.find(reverse("sample_app:posts-tagged", kwargs={"tag": tag.slug})) > -1)
            if tag.slug == "test-tag":
                rf = r"\s+{}\s+<span>\(\s+{} articles".format(tag.name, 2)
            else:
                rf = r"\s+{}\s+<span>\(\s+{} article".format(tag.name, 1)
            rx = re.compile(rf)
            self.assertEqual(len(rx.findall(rendered)), 1)

    def test_blog_archive_plugin(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].publish = True
        posts[0].save()
        posts[1].publish = True
        posts[1].save()
        ph = pages[0].placeholders.get(slot="content")
        plugin = add_plugin(ph, "BlogArchivePlugin", language="en", app_config=self.app_config_1)
        plugin_class = plugin.get_plugin_class_instance()

        context = self.get_plugin_context(pages[0], "en", plugin, edit=True)
        context = plugin_class.render(context, plugin, ph)
        self.assertEqual(
            context["dates"][0]["date"].date(), now().replace(year=now().year, month=now().month, day=1).date()
        )
        self.assertEqual(context["dates"][0]["count"], 2)

        posts[1].publish = False
        posts[1].save()
        context = plugin_class.render(context, plugin, ph)
        self.assertEqual(
            context["dates"][0]["date"].date(), now().replace(year=now().year, month=now().month, day=1).date()
        )
        self.assertEqual(context["dates"][0]["count"], 1)

    def test_templates(self):
        def _test_custom_templates_path(parts):
            templates_path = os.path.join(os.path.dirname(__file__), "test_utils", "templates")

            self.app_config_1.app_data.config.template_prefix = parts[0]
            self.app_config_1.save()
            tmp = plugin.template_folder
            plugin.template_folder = parts[1]
            plugin.save()
            dir_parts = (templates_path,) + parts
            template_parts = parts + (plugin_class.base_render_template,)
            try:
                os.makedirs(os.path.join(*dir_parts))
            except OSError:
                pass
            fake_template = os.path.join(*template_parts)
            with open(os.path.join(templates_path, fake_template), "w"):
                self.assertEqual(plugin_class.get_render_template(context, plugin, ph), fake_template)
            plugin.template_folder = tmp
            plugin.save()
            self.app_config_1.app_data.config.template_prefix = ""
            self.app_config_1.save()
            os.unlink(os.path.join(templates_path, fake_template))

        self.get_posts()
        pages = self.get_pages()

        ph = pages[0].placeholders.get(slot="content")
        plugin = add_plugin(ph, "BlogLatestEntriesPlugin", language="en", app_config=self.app_config_1)

        context = self.get_plugin_context(pages[0], "en", plugin)
        plugin_class = plugin.get_plugin_class_instance()
        self.assertEqual(
            plugin_class.get_render_template(context, plugin, ph),
            os.path.join("djangocms_blog", plugin.template_folder, plugin_class.base_render_template),
        )

        custom_parts = ("whatever", "whereever")
        _test_custom_templates_path(custom_parts)

        custom_parts = ("djangocms_blog", "whereever")
        _test_custom_templates_path(custom_parts)


class PluginTest10(BaseTest):
    def test_plugin_authors(self):
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].publish = True
        posts[0].save()
        posts[1].publish = True
        posts[1].save()
        ph = pages[0].placeholders.get(slot="content")
        plugin = add_plugin(ph, "BlogAuthorPostsPlugin", language="en", app_config=self.app_config_1)

        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertTrue(rendered.find("No author found") > -1)

        plugin.authors.add(self.user)
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertTrue(rendered.find("/en/page-two/author/admin/") > -1)
        self.assertTrue(rendered.find("2 articles") > -1)

        plugin.authors.add(self.user_staff)
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertTrue(rendered.find("/en/page-two/author/staff/") > -1)
        self.assertTrue(rendered.find("0 articles") > -1)

        plugin.authors.add(self.user_normal)
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertTrue(rendered.find("/en/page-two/author/normal/") > -1)
        self.assertTrue(rendered.find("0 articles") > -1)

        # Checking copy relations
        ph = pages[0].placeholders.get(slot="content")
        original = ph.get_plugins("en")
        pages[0].publish("en")
        published = pages[0].get_public_object()
        ph = published.placeholders.get(slot="content")
        new = ph.get_plugins("en")
        self.assertNotEqual(original, new)

        casted_authors, __ = new[0].get_plugin_instance()
        self.assertEqual(casted_authors.authors.count(), 3)

    def test_plugin_authors_admin(self):
        other_author = User.objects.create(username="other_author")
        non_author = User.objects.create(username="non_author")
        unpublished_author = User.objects.create(username="unpublished_author")
        pages = self.get_pages()
        posts = self.get_posts()
        posts[0].publish = True
        posts[0].save()
        posts[1].publish = True
        posts[1].author = other_author
        posts[1].save()
        posts[2].publish = False
        posts[2].author = unpublished_author
        posts[2].save()
        ph = pages[0].placeholders.get(slot="content")
        page_admin = admin.site._registry[Page]
        parms = {
            "cms_path": "/en/",
            "placeholder_id": ph.pk,
            "plugin_type": "BlogAuthorPostsPlugin",
            "plugin_language": "en",
        }
        path = "/en/?%s" % urlencode(parms)
        request = self.get_request(pages[0], "en", user=self.user, path=path)
        response = page_admin.add_plugin(request)
        form_authors = response.context_data["adminform"].form.fields["authors"].queryset
        self.assertEqual(form_authors.count(), 2)
        self.assertIn(other_author, form_authors)
        self.assertIn(self.user, form_authors)
        self.assertNotIn(unpublished_author, form_authors)
        self.assertNotIn(non_author, form_authors)

    def test_plugin_templates_field_single_template(self):
        pages = self.get_pages()
        ph = pages[0].placeholders.get(slot="content")
        plugins = [
            "BlogLatestEntriesPlugin",
            "BlogLatestEntriesPluginCached",
            "BlogAuthorPostsPlugin",
            "BlogAuthorPostsListPlugin",
            "BlogTagsPlugin",
            "BlogArchivePlugin",
            "BlogCategoryPlugin",
            "BlogFeaturedPostsPlugin",
            "BlogFeaturedPostsPluginCached",
        ]
        for plugin in plugins:
            page_admin = admin.site._registry[Page]
            parms = {
                "cms_path": "/en/",
                "placeholder_id": ph.pk,
                "plugin_type": plugin,
                "plugin_language": "en",
            }
            path = "/en/?%s" % urlencode(parms)
            request = self.get_request(pages[0], "en", user=self.user, path=path)
            response = page_admin.add_plugin(request)
            with self.assertRaises(KeyError):
                template_folder_field = response.context_data["adminform"].form.fields["template_folder"]  # noqa: F841

    @override_settings(
        BLOG_PLUGIN_TEMPLATE_FOLDERS=(
            ("default", "Default template"),
            ("vertical", "Vertical timeline"),
        )
    )
    def test_plugin_templates_field_multi_template(self):
        pages = self.get_pages()
        ph = pages[0].placeholders.get(slot="content")
        plugins = [
            "BlogLatestEntriesPlugin",
            "BlogLatestEntriesPluginCached",
            "BlogAuthorPostsPlugin",
            "BlogAuthorPostsListPlugin",
            "BlogTagsPlugin",
            "BlogArchivePlugin",
            "BlogCategoryPlugin",
            "BlogFeaturedPostsPlugin",
            "BlogFeaturedPostsPluginCached",
        ]
        for plugin in plugins:
            page_admin = admin.site._registry[Page]
            parms = {
                "cms_path": "/en/",
                "placeholder_id": ph.pk,
                "plugin_type": plugin,
                "plugin_language": "en",
            }
            path = "/en/?%s" % urlencode(parms)
            request = self.get_request(pages[0], "en", user=self.user, path=path)
            response = page_admin.add_plugin(request)
            template_folder_field = response.context_data["adminform"].form.fields["template_folder"]
            self.assertEqual(len(template_folder_field.choices), 2)
            self.assertEqual(sorted(dict(template_folder_field.choices).keys()), sorted(["default", "vertical"]))


class PluginTest2(BaseTest):
    def test_blog_category_plugin(self):
        pages = self.get_pages()
        posts = self.get_posts()
        self.category_1.set_current_language("en")
        posts[0].publish = True
        posts[0].save()
        posts[1].publish = True
        posts[1].save()
        posts[1].sites.add(self.site_2)
        new_category = BlogCategory.objects.create(name="category 2", app_config=self.app_config_1)
        posts[1].categories.add(new_category)

        ph = pages[0].placeholders.get(slot="content")
        plugin = add_plugin(ph, "BlogCategoryPlugin", language="en", app_config=self.app_config_1)
        plugin_class = plugin.get_plugin_class_instance()
        context = self.get_plugin_context(pages[0], "en", plugin, edit=True)
        context = plugin_class.render(context, plugin, ph)
        self.assertTrue(context["categories"])
        self.assertEqual(list(context["categories"]), [self.category_1])

        plugin.current_site = False
        plugin.save()
        context = plugin_class.render(context, plugin, ph)
        self.assertEqual(list(context["categories"]), [self.category_1, new_category])

        plugin.current_site = True
        plugin.save()
        with self.settings(SITE_ID=2):
            context = plugin_class.render(context, plugin, ph)
            self.assertEqual(list(context["categories"]), [self.category_1, new_category])

        plugin.current_site = False
        plugin.save()
        with self.settings(SITE_ID=2):
            context = plugin_class.render(context, plugin, ph)
            self.assertEqual(list(context["categories"]), [self.category_1, new_category])

        empty_category = BlogCategory.objects.create(name="empty 2", app_config=self.app_config_1)
        self.app_config_1.app_data.config.menu_empty_categories = False
        self.app_config_1.save()
        context = plugin_class.render(context, plugin, ph)
        self.assertEqual(list(context["categories"]), [self.category_1, new_category])

        self.app_config_1.app_data.config.menu_empty_categories = True
        self.app_config_1.save()
        context = plugin_class.render(context, plugin, ph)
        self.assertEqual(list(context["categories"]), [self.category_1, new_category, empty_category])


class PluginTestNamespace(BaseTest):
    def test_plugin_latest_namespace(self):
        pages = self.get_pages()
        posts = self.get_posts()
        self.category_1.set_current_language("en")
        category_2 = BlogCategory.objects.create(name="category 2", app_config=self.app_config_2)
        category_2.set_current_language("en")
        ph = pages[0].placeholders.get(slot="content")
        plugin = add_plugin(ph, "BlogLatestEntriesPlugin", language="en", app_config=self.app_config_1)
        plugin.categories.add(self.category_1)
        plugin.save()
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertTrue(
            rendered.find(reverse("sample_app:posts-category", kwargs={"category": self.category_1.slug})) > -1
        )
        self.assertFalse(
            rendered.find(reverse("sample_app2:posts-category", kwargs={"category": category_2.slug})) > -1
        )
        plugin.categories.add(category_2)
        plugin.save()
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertTrue(
            rendered.find(reverse("sample_app:posts-category", kwargs={"category": self.category_1.slug})) > -1
        )
        self.assertFalse(
            rendered.find(reverse("sample_app2:posts-category", kwargs={"category": category_2.slug})) > -1
        )
        plugin.app_config = self.app_config_2
        plugin.save()
        posts[3].categories.remove(self.category_1)
        posts[3].categories.add(category_2)
        posts[3].save()
        rendered = self.render_plugin(pages[0], "en", plugin, edit=True)
        self.assertFalse(
            rendered.find(reverse("sample_app:posts-category", kwargs={"category": self.category_1.slug})) > -1
        )
        self.assertTrue(
            rendered.find(reverse("sample_app2:posts-category", kwargs={"category": category_2.slug})) > -1
        )
