# -*- coding: utf-8 -*-
import datetime

from django.core.urlresolvers import resolve
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView
from hvad.admin import TranslatableModelAdminMixin

from .models import Post


class BaseBlogView(TranslatableModelAdminMixin):

    def get_queryset(self):
        language = self._language(self.request)
        manager = self.model._default_manager.language(language)
        if not self.request.user.is_staff:
            manager = manager.published()
        return manager

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['current_app'] = resolve(self.request.path).namespace
        return super(BaseBlogView, self).render_to_response(context, **response_kwargs)


class PostListView(BaseBlogView, ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = "djangocms_blog/post_list.html"


class PostDetailView(BaseBlogView, DetailView):
    model = Post
    context_object_name = 'post'
    template_name = "djangocms_blog/post_detail.html"


class PostArchiveView(BaseBlogView, ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = "djangocms_blog/post_list.html"
    date_field = 'date_published'
    allow_empty = True
    allow_future = True

    def get_queryset(self):
        qs = super(PostArchiveView, self).get_queryset()
        if 'month' in self.kwargs:
            qs = qs.filter(**{"%s__month" % self.date_field: self.kwargs['month']})
        if 'year' in self.kwargs:
            qs = qs.filter(**{"%s__year" % self.date_field: self.kwargs['year']})
        return qs

    def get_context_data(self, **kwargs):
        kwargs['month'] = int(self.kwargs.get('month')) if 'month' in self.kwargs else None
        kwargs['year'] = int(self.kwargs.get('year')) if 'year' in self.kwargs else None
        if kwargs['year']:
            kwargs['archive_date'] = datetime.date(kwargs['year'], kwargs['month'] or 1, 1)
        return super(PostArchiveView, self).get_context_data(**kwargs)


class TaggedListView(BaseBlogView, ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = "djangocms_blog/post_list.html"

    def get_queryset(self):
        qs = super(TaggedListView, self).get_queryset()
        return qs.filter(tags__slug=self.kwargs['tag'])

    def get_context_data(self, **kwargs):
        kwargs['tagged_entries'] = (self.kwargs.get('tag')
                                    if 'tag' in self.kwargs else None)
        return super(TaggedListView, self).get_context_data(**kwargs)


class AuthorEntriesView(BaseBlogView, ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = "djangocms_blog/post_list.html"

    def get_queryset(self):
        qs = super(AuthorEntriesView, self).get_queryset()
        if 'username' in self.kwargs:
            qs = qs.filter(author__username=self.kwargs['username'])
        return qs

    def get_context_data(self, **kwargs):
        kwargs['author'] = self.kwargs.get('username')
        return super(AuthorEntriesView, self).get_context_data(**kwargs)
