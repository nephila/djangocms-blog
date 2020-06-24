import os.path

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.template.loader import select_template

from .forms import AuthorPostsForm, BlogPluginForm, LatestEntriesForm
from .models import AuthorEntriesPlugin, BlogCategory, GenericBlogPlugin, LatestPostsPlugin, Post
from .settings import get_setting


class BlogPlugin(CMSPluginBase):
    module = get_setting("PLUGIN_MODULE_NAME")
    form = BlogPluginForm

    def get_render_template(self, context, instance, placeholder):
        """
        Select the template used to render the plugin.

        Check the default folder as well as the folders provided to the apphook config.
        """
        templates = [os.path.join("djangocms_blog", instance.template_folder, self.base_render_template)]
        if instance.app_config and instance.app_config.template_prefix:
            templates.insert(
                0,
                os.path.join(instance.app_config.template_prefix, instance.template_folder, self.base_render_template),
            )

        selected = select_template(templates)
        return selected.template.name


@plugin_pool.register_plugin
class BlogLatestEntriesPlugin(BlogPlugin):
    """
    Return the latest published posts which bypasses cache,  taking into account the user / toolbar state.
    """

    name = get_setting("LATEST_ENTRIES_PLUGIN_NAME")
    model = LatestPostsPlugin
    form = LatestEntriesForm
    filter_horizontal = ("categories",)
    cache = False
    base_render_template = "latest_entries.html"

    def get_fields(self, request, obj=None):
        """
        Return the fields available when editing the plugin.

        'template_folder' field is added if ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` contains multiple folders.

        """
        fields = ["app_config", "latest_posts", "tags", "categories"]
        if len(get_setting("PLUGIN_TEMPLATE_FOLDERS")) > 1:
            fields.append("template_folder")
        return fields

    def render(self, context, instance, placeholder):
        """Render the plugin."""
        context = super().render(context, instance, placeholder)
        context["posts_list"] = instance.get_posts(context["request"], published_only=False)
        context["TRUNCWORDS_COUNT"] = get_setting("POSTS_LIST_TRUNCWORDS_COUNT")
        return context


@plugin_pool.register_plugin
class BlogLatestEntriesPluginCached(BlogLatestEntriesPlugin):
    """
    Return the latest published posts caching the result.
    """

    name = get_setting("LATEST_ENTRIES_PLUGIN_NAME_CACHED")
    cache = True


@plugin_pool.register_plugin
class BlogAuthorPostsPlugin(BlogPlugin):
    """Render the list of authors."""

    module = get_setting("PLUGIN_MODULE_NAME")
    name = get_setting("AUTHOR_POSTS_PLUGIN_NAME")
    model = AuthorEntriesPlugin
    form = AuthorPostsForm
    base_render_template = "authors.html"
    filter_horizontal = ["authors"]

    def get_fields(self, request, obj=None):
        """
        Return the fields available when editing the plugin.

        'template_folder' field is added if ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` contains multiple folders.

        """
        fields = ["app_config", "current_site", "authors"]
        if len(get_setting("PLUGIN_TEMPLATE_FOLDERS")) > 1:
            fields.append("template_folder")
        return fields

    def render(self, context, instance, placeholder):
        """Render the plugin."""
        context = super().render(context, instance, placeholder)
        context["authors_list"] = instance.get_authors(context["request"])
        return context


@plugin_pool.register_plugin
class BlogAuthorPostsListPlugin(BlogAuthorPostsPlugin):
    """Render the list of posts for each selected author."""

    name = get_setting("AUTHOR_POSTS_LIST_PLUGIN_NAME")
    base_render_template = "authors_posts.html"
    fields = (
        ["app_config", "current_site", "authors", "latest_posts"] + ["template_folder"]
        if len(get_setting("PLUGIN_TEMPLATE_FOLDERS")) > 1
        else []
    )

    def get_fields(self, request, obj=None):
        """
        Return the fields available when editing the plugin.

        'template_folder' field is added if ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` contains multiple folders.

        """
        fields = ["app_config", "current_site", "authors", "latest_posts"]
        if len(get_setting("PLUGIN_TEMPLATE_FOLDERS")) > 1:
            fields.append("template_folder")
        return fields


@plugin_pool.register_plugin
class BlogTagsPlugin(BlogPlugin):
    """Render the list of post tags."""

    module = get_setting("PLUGIN_MODULE_NAME")
    name = get_setting("TAGS_PLUGIN_NAME")
    model = GenericBlogPlugin
    base_render_template = "tags.html"

    def get_exclude(self, request, obj=None):
        """Exclude 'template_folder' field if ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` contains one folder."""
        return [] if len(get_setting("PLUGIN_TEMPLATE_FOLDERS")) > 1 else ["template_folder"]

    def render(self, context, instance, placeholder):
        """Render the plugin."""
        context = super().render(context, instance, placeholder)
        qs = instance.post_queryset(context["request"])
        context["tags"] = Post.objects.tag_cloud(queryset=qs.published())
        return context


@plugin_pool.register_plugin
class BlogCategoryPlugin(BlogPlugin):
    """Render the list of post categories."""

    module = get_setting("PLUGIN_MODULE_NAME")
    name = get_setting("CATEGORY_PLUGIN_NAME")
    model = GenericBlogPlugin
    base_render_template = "categories.html"

    def get_exclude(self, request, obj=None):
        """Exclude 'template_folder' field if ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` contains one folder."""
        return [] if len(get_setting("PLUGIN_TEMPLATE_FOLDERS")) > 1 else ["template_folder"]

    def render(self, context, instance, placeholder):
        """Render the plugin."""
        context = super().render(context, instance, placeholder)
        qs = BlogCategory.objects.active_translations()
        if instance.app_config:
            qs = qs.namespace(instance.app_config.namespace)
        if instance.current_site:
            site = get_current_site(context["request"])
            qs = qs.filter(models.Q(blog_posts__sites__isnull=True) | models.Q(blog_posts__sites=site.pk))
        categories = qs.distinct()
        if instance.app_config and not instance.app_config.menu_empty_categories:
            categories = qs.filter(blog_posts__isnull=False).distinct()
        context["categories"] = categories
        return context


@plugin_pool.register_plugin
class BlogArchivePlugin(BlogPlugin):
    """Render the list of months with available posts."""

    module = get_setting("PLUGIN_MODULE_NAME")
    name = get_setting("ARCHIVE_PLUGIN_NAME")
    model = GenericBlogPlugin
    base_render_template = "archive.html"

    def get_exclude(self, request, obj=None):
        """Exclude 'template_folder' field if ``BLOG_PLUGIN_TEMPLATE_FOLDERS`` contains one folder."""
        return [] if len(get_setting("PLUGIN_TEMPLATE_FOLDERS")) > 1 else ["template_folder"]

    def render(self, context, instance, placeholder):
        """Render the plugin."""
        context = super().render(context, instance, placeholder)
        qs = instance.post_queryset(context["request"])
        context["dates"] = Post.objects.get_months(queryset=qs.published())
        return context
