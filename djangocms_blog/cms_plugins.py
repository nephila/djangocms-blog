# -*- coding: utf-8 -*-
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .forms import LatestEntriesForm
from .models import AuthorEntriesPlugin, BlogCategory, LatestPostsPlugin, Post
from .settings import get_setting


class BlogPlugin(CMSPluginBase):
    module = 'Blog'


class BlogLatestEntriesPlugin(BlogPlugin):
    """
    Non cached plugin which returns the latest posts taking into account the
      user / toolbar state
    """
    render_template = 'djangocms_blog/plugins/latest_entries.html'
    name = _('Latest Blog Articles')
    model = LatestPostsPlugin
    form = LatestEntriesForm
    filter_horizontal = ('categories',)
    cache = False

    def render(self, context, instance, placeholder):
        context = super(BlogLatestEntriesPlugin, self).render(context, instance, placeholder)
        context['posts_list'] = instance.get_posts(context['request'])
        context['TRUNCWORDS_COUNT'] = get_setting('POSTS_LIST_TRUNCWORDS_COUNT')
        return context


class BlogLatestEntriesPluginCached(BlogPlugin):
    """
    Cached plugin which returns the latest published posts
    """
    render_template = 'djangocms_blog/plugins/latest_entries.html'
    name = _('Latest Blog Articles')
    model = LatestPostsPlugin
    form = LatestEntriesForm
    filter_horizontal = ('categories',)

    def render(self, context, instance, placeholder):
        context = super(BlogLatestEntriesPluginCached, self).render(context, instance, placeholder)
        context['posts_list'] = instance.get_posts()
        context['TRUNCWORDS_COUNT'] = get_setting('POSTS_LIST_TRUNCWORDS_COUNT')
        return context


class BlogAuthorPostsPlugin(BlogPlugin):
    module = _('Blog')
    name = _('Author Blog Articles')
    model = AuthorEntriesPlugin
    form = LatestEntriesForm
    render_template = 'djangocms_blog/plugins/authors.html'
    filter_horizontal = ['authors']

    def render(self, context, instance, placeholder):
        context = super(BlogAuthorPostsPlugin, self).render(context, instance, placeholder)
        context['authors_list'] = instance.get_authors()
        return context


class BlogTagsPlugin(BlogPlugin):
    module = _('Blog')
    name = _('Tags')
    model = CMSPlugin
    render_template = 'djangocms_blog/plugins/tags.html'

    def render(self, context, instance, placeholder):
        context = super(BlogTagsPlugin, self).render(context, instance, placeholder)
        context['tags'] = Post.objects.tag_cloud(queryset=Post.objects.published())
        return context


class BlogCategoryPlugin(BlogPlugin):
    module = _('Blog')
    name = _('Categories')
    model = CMSPlugin
    render_template = 'djangocms_blog/plugins/categories.html'

    def render(self, context, instance, placeholder):
        context = super(BlogCategoryPlugin, self).render(context, instance, placeholder)
        context['categories'] = BlogCategory.objects.all()
        return context


class BlogArchivePlugin(BlogPlugin):
    module = _('Blog')
    name = _('Archive')
    model = CMSPlugin
    render_template = 'djangocms_blog/plugins/archive.html'

    def render(self, context, instance, placeholder):
        context = super(BlogArchivePlugin, self).render(context, instance, placeholder)
        context['dates'] = Post.objects.get_months(queryset=Post.objects.published())
        return context


plugin_pool.register_plugin(BlogLatestEntriesPlugin)
plugin_pool.register_plugin(BlogAuthorPostsPlugin)
plugin_pool.register_plugin(BlogTagsPlugin)
plugin_pool.register_plugin(BlogArchivePlugin)
plugin_pool.register_plugin(BlogCategoryPlugin)
