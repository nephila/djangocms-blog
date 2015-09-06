# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os.path

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .forms import LatestEntriesForm
from .models import AuthorEntriesPlugin, BlogCategory, GenericBlogPlugin, LatestPostsPlugin, Post
from .settings import get_setting


class BlogPlugin(CMSPluginBase):
    module = 'Blog'

    def get_render_template(self, context, instance, placeholder):
        if instance.app_config.template_prefix:
            return os.path.join(instance.app_config.template_prefix, self.base_render_template)
        else:
            return os.path.join('djangocms_blog', self.base_render_template)


class BlogLatestEntriesPlugin(BlogPlugin):
    """
    Non cached plugin which returns the latest posts taking into account the
      user / toolbar state
    """
    name = _('Latest Blog Articles')
    model = LatestPostsPlugin
    form = LatestEntriesForm
    filter_horizontal = ('categories',)
    fields = ('latest_posts', 'tags', 'categories')
    cache = False
    base_render_template = 'plugins/latest_entries.html'

    def render(self, context, instance, placeholder):
        context = super(BlogLatestEntriesPlugin, self).render(context, instance, placeholder)
        context['posts_list'] = instance.get_posts(context['request'])
        context['TRUNCWORDS_COUNT'] = get_setting('POSTS_LIST_TRUNCWORDS_COUNT')
        return context


class BlogLatestEntriesPluginCached(BlogPlugin):
    """
    Cached plugin which returns the latest published posts
    """
    name = _('Latest Blog Articles')
    model = LatestPostsPlugin
    form = LatestEntriesForm
    filter_horizontal = ('categories',)
    fields = ('latest_posts', 'tags', 'categories')
    base_render_template = 'plugins/latest_entries.html'

    def render(self, context, instance, placeholder):
        context = super(BlogLatestEntriesPluginCached, self).render(context, instance, placeholder)
        context['posts_list'] = instance.get_posts()
        context['TRUNCWORDS_COUNT'] = get_setting('POSTS_LIST_TRUNCWORDS_COUNT')
        return context


class BlogAuthorPostsPlugin(BlogPlugin):
    module = _('Blog')
    name = _('Author Blog Articles')
    model = AuthorEntriesPlugin
    base_render_template = 'plugins/authors.html'
    filter_horizontal = ['authors']

    def render(self, context, instance, placeholder):
        context = super(BlogAuthorPostsPlugin, self).render(context, instance, placeholder)
        context['authors_list'] = instance.get_authors()
        return context


class BlogTagsPlugin(BlogPlugin):
    module = _('Blog')
    name = _('Tags')
    model = GenericBlogPlugin
    base_render_template = 'plugins/tags.html'

    def render(self, context, instance, placeholder):
        context = super(BlogTagsPlugin, self).render(context, instance, placeholder)
        qs = Post._default_manager
        qs_post = qs
        if instance.app_config:
            qs_post = qs_post.namespace(instance.app_config.namespace)
        context['tags'] = qs.tag_cloud(queryset=qs_post.published())
        return context


class BlogCategoryPlugin(BlogPlugin):
    module = _('Blog')
    name = _('Categories')
    model = GenericBlogPlugin
    base_render_template = 'plugins/categories.html'

    def render(self, context, instance, placeholder):
        context = super(BlogCategoryPlugin, self).render(context, instance, placeholder)
        qs = BlogCategory._default_manager
        if instance.app_config:
            qs = qs.namespace(instance.app_config.namespace)
        context['categories'] = qs
        return context


class BlogArchivePlugin(BlogPlugin):
    module = _('Blog')
    name = _('Archive')
    model = GenericBlogPlugin
    base_render_template = 'plugins/archive.html'

    def render(self, context, instance, placeholder):
        context = super(BlogArchivePlugin, self).render(context, instance, placeholder)
        qs = Post._default_manager
        qs_post = qs
        if instance.app_config:
            qs_post = qs.namespace(instance.app_config.namespace)
        context['dates'] = qs.get_months(queryset=qs_post.published())
        return context


plugin_pool.register_plugin(BlogLatestEntriesPlugin)
plugin_pool.register_plugin(BlogAuthorPostsPlugin)
plugin_pool.register_plugin(BlogTagsPlugin)
plugin_pool.register_plugin(BlogArchivePlugin)
plugin_pool.register_plugin(BlogCategoryPlugin)
