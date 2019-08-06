# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os.path

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib.sites.shortcuts import get_current_site
from django.db import models

from .forms import LatestEntriesForm
from .models import AuthorEntriesPlugin, BlogCategory, GenericBlogPlugin, LatestPostsPlugin, Post
from .settings import get_setting


class BlogPlugin(CMSPluginBase):
    module = get_setting('PLUGIN_MODULE_NAME')

    def get_render_template(self, context, instance, placeholder):
        if instance.app_config and instance.app_config.template_prefix:
            return os.path.join(instance.app_config.template_prefix,
                                instance.template_folder,
                                self.base_render_template)
        else:
            return os.path.join('djangocms_blog',
                                instance.template_folder,
                                self.base_render_template)


class BlogLatestEntriesPlugin(BlogPlugin):
    """
    Non cached plugin which returns the latest posts taking into account the
      user / toolbar state
    """
    name = get_setting('LATEST_ENTRIES_PLUGIN_NAME')
    model = LatestPostsPlugin
    form = LatestEntriesForm
    filter_horizontal = ('categories',)
    fields = ['app_config', 'latest_posts', 'tags', 'categories'] + \
        ['template_folder'] if len(get_setting('PLUGIN_TEMPLATE_FOLDERS')) > 1 else []
    cache = False
    base_render_template = 'latest_entries.html'

    def render(self, context, instance, placeholder):
        context = super(BlogLatestEntriesPlugin, self).render(context, instance, placeholder)
        context['posts_list'] = instance.get_posts(context['request'], published_only=False)
        context['TRUNCWORDS_COUNT'] = get_setting('POSTS_LIST_TRUNCWORDS_COUNT')
        return context


class BlogLatestEntriesPluginCached(BlogPlugin):
    """
    Cached plugin which returns the latest published posts
    """
    name = get_setting('LATEST_ENTRIES_PLUGIN_NAME_CACHED')
    model = LatestPostsPlugin
    form = LatestEntriesForm
    filter_horizontal = ('categories',)
    fields = ['app_config', 'latest_posts', 'tags', 'categories'] + \
        ['template_folder'] if len(get_setting('PLUGIN_TEMPLATE_FOLDERS')) > 1 else []
    base_render_template = 'latest_entries.html'

    def render(self, context, instance, placeholder):
        context = super(BlogLatestEntriesPluginCached, self).render(context, instance, placeholder)
        context['posts_list'] = instance.get_posts(context['request'])
        context['TRUNCWORDS_COUNT'] = get_setting('POSTS_LIST_TRUNCWORDS_COUNT')
        return context


class BlogAuthorPostsPlugin(BlogPlugin):
    module = get_setting('PLUGIN_MODULE_NAME')
    name = get_setting('AUTHOR_POSTS_PLUGIN_NAME')
    model = AuthorEntriesPlugin
    base_render_template = 'authors.html'
    filter_horizontal = ['authors']
    exclude = ['template_folder'] if len(get_setting('PLUGIN_TEMPLATE_FOLDERS')) >= 1 else []

    def render(self, context, instance, placeholder):
        context = super(BlogAuthorPostsPlugin, self).render(context, instance, placeholder)
        context['authors_list'] = instance.get_authors()
        return context


class BlogTagsPlugin(BlogPlugin):
    module = get_setting('PLUGIN_MODULE_NAME')
    name = get_setting('TAGS_PLUGIN_NAME')
    model = GenericBlogPlugin
    base_render_template = 'tags.html'
    exclude = ['template_folder'] if len(get_setting('PLUGIN_TEMPLATE_FOLDERS')) >= 1 else []

    def render(self, context, instance, placeholder):
        context = super(BlogTagsPlugin, self).render(context, instance, placeholder)
        qs = instance.post_queryset(context['request'])
        context['tags'] = Post.objects.tag_cloud(queryset=qs.published())
        return context


class BlogCategoryPlugin(BlogPlugin):
    module = get_setting('PLUGIN_MODULE_NAME')
    name = get_setting('CATEGORY_PLUGIN_NAME')
    model = GenericBlogPlugin
    base_render_template = 'categories.html'
    exclude = ['template_folder'] if len(get_setting('PLUGIN_TEMPLATE_FOLDERS')) >= 1 else []

    def render(self, context, instance, placeholder):
        context = super(BlogCategoryPlugin, self).render(context, instance, placeholder)
        qs = BlogCategory.objects.language().active_translations()
        if instance.app_config:
            qs = qs.namespace(instance.app_config.namespace)
        if instance.current_site:
            site = get_current_site(context['request'])
            qs = qs.filter(
                models.Q(blog_posts__sites__isnull=True) | models.Q(blog_posts__sites=site.pk)
            )
        categories = qs.distinct()
        if instance.app_config and not instance.app_config.menu_empty_categories:
            categories = qs.filter(blog_posts__isnull=False).distinct()
        context['categories'] = categories
        return context


class BlogArchivePlugin(BlogPlugin):
    module = get_setting('PLUGIN_MODULE_NAME')
    name = get_setting('ARCHIVE_PLUGIN_NAME')
    model = GenericBlogPlugin
    base_render_template = 'archive.html'
    exclude = ['template_folder'] if len(get_setting('PLUGIN_TEMPLATE_FOLDERS')) >= 1 else []

    def render(self, context, instance, placeholder):
        context = super(BlogArchivePlugin, self).render(context, instance, placeholder)
        qs = instance.post_queryset(context['request'])
        context['dates'] = Post.objects.get_months(queryset=qs.published())
        return context


plugin_pool.register_plugin(BlogLatestEntriesPlugin)
plugin_pool.register_plugin(BlogLatestEntriesPluginCached)
plugin_pool.register_plugin(BlogAuthorPostsPlugin)
plugin_pool.register_plugin(BlogTagsPlugin)
plugin_pool.register_plugin(BlogArchivePlugin)
plugin_pool.register_plugin(BlogCategoryPlugin)
