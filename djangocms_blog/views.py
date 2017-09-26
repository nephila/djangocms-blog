# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os.path

from aldryn_apphooks_config.mixins import AppConfigMixin
from cms.models.fields import PlaceholderField
from cms.utils import get_language_list, copy_plugins
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponse
from django.utils.encoding import force_text
from django.utils.timezone import now
from django.utils.translation import get_language
from django.views.generic import DetailView, ListView
from parler.views import TranslatableSlugMixin, ViewUrlMixin
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from .models import BlogCategory, Post
from taggit.models import Tag
from .settings import get_setting

User = get_user_model()


class BaseBlogView(AppConfigMixin, ViewUrlMixin):
    model = Post

    def optimize(self, qs):
        """
        Apply select_related / prefetch_related to optimize the view queries
        :param qs: queryset to optimize
        :return: optimized queryset
        """
        return qs.select_related('app_config').prefetch_related(
            'translations', 'categories', 'categories__translations', 'categories__app_config'
        )

    def get_view_url(self):
        if not self.view_url_name:
            raise ImproperlyConfigured(
                'Missing `view_url_name` attribute on {0}'.format(self.__class__.__name__)
            )

        url = reverse(
            self.view_url_name,
            args=self.args,
            kwargs=self.kwargs,
            current_app=self.namespace
        )
        return self.request.build_absolute_uri(url)

    def get_queryset(self):
        language = get_language()
        queryset = self.model._default_manager.active_translations(
            language_code=language
        )
        if not getattr(self.request, 'toolbar', False) or not self.request.toolbar.edit_mode:
            queryset = queryset.published()
        setattr(self.request, get_setting('CURRENT_NAMESPACE'), self.config)
        return self.optimize(queryset.on_site())

    def get_template_names(self):
        template_path = (self.config and self.config.template_prefix) or 'djangocms_blog'
        return os.path.join(template_path, self.base_template_name)

    def get_context_data(self, **kwargs):
        context = super(BaseBlogView, self).get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        context['tags_list'] = Tag.objects.all()
        return context


class BaseBlogListView(BaseBlogView):
    context_object_name = 'post_list'
    base_template_name = 'post_list.html'

    def get_context_data(self, **kwargs):
        context = super(BaseBlogListView, self).get_context_data(**kwargs)
        context['TRUNCWORDS_COUNT'] = get_setting('POSTS_LIST_TRUNCWORDS_COUNT')
        return context

    def get_paginate_by(self, queryset):
        return (self.config and self.config.paginate_by) or get_setting('PAGINATION')


class PostDetailView(TranslatableSlugMixin, BaseBlogView, DetailView):
    context_object_name = 'post'
    base_template_name = 'post_detail.html'
    slug_field = 'slug'
    view_url_name = 'djangocms_blog:post-detail'
    instant_article = False

    def liveblog_enabled(self):
        return self.object.enable_liveblog and apps.is_installed('djangocms_blog.liveblog')

    def get_template_names(self):
        if self.instant_article:
            template_path = (self.config and self.config.template_prefix) or 'djangocms_blog'
            return os.path.join(template_path, 'post_instant_article.html')
        else:
            return super(PostDetailView, self).get_template_names()

    def get_queryset(self):
        queryset = self.model._default_manager.all()
        if not getattr(self.request, 'toolbar', False) or not self.request.toolbar.edit_mode:
            queryset = queryset.published()
        return self.optimize(queryset)

    def get(self, *args, **kwargs):
        # submit object to cms to get corrent language switcher and selected category behavior
        if hasattr(self.request, 'toolbar'):
            self.request.toolbar.set_object(self.get_object())
        return super(PostDetailView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta()
        context['instant_article'] = self.instant_article
        context['use_placeholder'] = get_setting('USE_PLACEHOLDER')
        setattr(self.request, get_setting('CURRENT_POST_IDENTIFIER'), self.get_object())
        return context


class PostListView(BaseBlogListView, ListView):
    view_url_name = 'djangocms_blog:posts-latest'


class PostArchiveView(BaseBlogListView, ListView):
    date_field = 'date_published'
    allow_empty = True
    allow_future = True
    view_url_name = 'djangocms_blog:posts-archive'

    def get_queryset(self):
        qs = super(PostArchiveView, self).get_queryset()
        if 'month' in self.kwargs:
            qs = qs.filter(**{'%s__month' % self.date_field: self.kwargs['month']})
        if 'year' in self.kwargs:
            qs = qs.filter(**{'%s__year' % self.date_field: self.kwargs['year']})
        return self.optimize(qs)

    def get_context_data(self, **kwargs):
        kwargs['month'] = int(self.kwargs.get('month')) if 'month' in self.kwargs else None
        kwargs['year'] = int(self.kwargs.get('year')) if 'year' in self.kwargs else None
        if kwargs['year']:
            kwargs['archive_date'] = now().replace(kwargs['year'], kwargs['month'] or 1, 1)
        context = super(PostArchiveView, self).get_context_data(**kwargs)
        return context


class RecommendedPostsView(PostListView):
    def get_queryset(self):
        query = Post.objects.filter(recommended=True).order_by('-date_published')
        self.count = query.count()
        if self.request.is_ajax():
            query = query[self.get_offset(self.request):(self.get_offset(self.request)+self.get_limit(self.request))]
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'list_name': 'Odporúčané'
        })
        return context


class MostReadPostsView(PostListView):
    def get_queryset(self):
        query = sorted(Post.objects.all(), key=lambda x: x.get_hits(), reverse=True)
        self.count = Post.objects.all()
        if self.request.is_ajax():
            query = query[self.get_offset(self.request):(self.get_offset(self.request)+self.get_limit(self.request))]
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'list_name': 'Najčítanejšie'
        })
        return context


class FavouritesPostsView(PostListView):
    def get_queryset(self):
        query = Post.objects.all().order_by('-date_created')
        self.count = query.count()
        if self.request.is_ajax():
            query = query[self.get_offset(self.request):(self.get_offset(self.request)+self.get_limit(self.request))]
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'list_name': 'Najnovšie'
        })
        return context


class TaggedListView(BaseBlogListView, ListView):
    view_url_name = 'djangocms_blog:posts-tagged'

    def get_queryset(self):
        qs = super(TaggedListView, self).get_queryset()
        return self.optimize(qs.filter(tags__slug=self.kwargs['tag']))

    def get_context_data(self, **kwargs):
        kwargs['tagged_entries'] = (self.kwargs.get('tag')
                                    if 'tag' in self.kwargs else None)
        context = super(TaggedListView, self).get_context_data(**kwargs)
        return context


class AuthorEntriesView(BaseBlogListView, ListView):
    view_url_name = 'djangocms_blog:posts-author'

    def get_queryset(self):
        qs = super(AuthorEntriesView, self).get_queryset()
        if 'username' in self.kwargs:
            qs = qs.filter(**{'author__%s' % User.USERNAME_FIELD: self.kwargs['username']})
        return self.optimize(qs)

    def get_context_data(self, **kwargs):
        kwargs['author'] = User.objects.get(**{User.USERNAME_FIELD: self.kwargs.get('username')})
        context = super(AuthorEntriesView, self).get_context_data(**kwargs)
        return context


class CategoryEntriesView(BaseBlogListView, ListView):
    _category = None
    view_url_name = 'djangocms_blog:posts-category'

    @property
    def category(self):
        if not self._category:
            self._category = get_object_or_404(
                BlogCategory,
                translations__slug=self.kwargs['category']
            )
        return self._category

    def get(self, *args, **kwargs):
        # submit object to cms toolbar to get correct language switcher behavior
        if hasattr(self.request, 'toolbar'):
            self.request.toolbar.set_object(self.category)
        return super(CategoryEntriesView, self).get(*args, **kwargs)

    def get_queryset(self):
        qs = super(CategoryEntriesView, self).get_queryset()
        if 'category' in self.kwargs:
            qs = qs.filter(categories=self.category.pk)
        return self.optimize(qs)

    def get_context_data(self, **kwargs):
        kwargs['category'] = self.category
        context = super(CategoryEntriesView, self).get_context_data(**kwargs)
        context['meta'] = self.category.as_meta()
        return context


@transaction.atomic
def copy_language(request, post_id):
    source_language = request.POST.get('source_language')
    target_language = request.POST.get('target_language')
    post = Post.objects.get(pk=post_id)

    if not target_language or target_language not in get_language_list():
        return HttpResponseBadRequest(
            force_text(_("Language must be set to a supported language!"))
        )

    placeholders = []
    for field in Post._meta.get_fields():
        if type(field) is PlaceholderField:
            placeholders.append(field.name)
    for placeholder_field_name in placeholders:
        placeholder = getattr(post, placeholder_field_name)
        if not placeholder:
            continue
        plugins = list(
            placeholder.cmsplugin_set.filter(language=source_language).order_by('path'))
        copy_plugins.copy_plugins_to(plugins, placeholder, target_language)
    return HttpResponse("ok")
