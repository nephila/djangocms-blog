# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import get_language
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.http import Http404
from django.views.generic import ListView, DetailView
from parler.utils import get_active_language_choices

from parler.views import ViewUrlMixin

from .models import Post, BlogCategory, BLOG_CURRENT_POST_IDENTIFIER
from .settings import BLOG_PAGINATION, BLOG_POSTS_LIST_TRUNCWORDS_COUNT


class BaseBlogView(ViewUrlMixin):

    def get_queryset(self):
        language = get_language()
        manager = self.model._default_manager.language(language)
        if not self.request.user.is_staff:
            manager = manager.filter(publish=True)
        return manager

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['current_app'] = resolve(self.request.path).namespace
        return super(BaseBlogView, self).render_to_response(context, **response_kwargs)


class PostListView(BaseBlogView, ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = "djangocms_blog/post_list.html"
    paginate_by = BLOG_PAGINATION
    view_url_name = 'djangocms_blog:posts-latest'

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['TRUNCWORDS_COUNT'] = BLOG_POSTS_LIST_TRUNCWORDS_COUNT
        return context


class PostDetailView(BaseBlogView, DetailView):
    model = Post
    context_object_name = 'post'
    template_name = "djangocms_blog/post_detail.html"
    slug_field = 'slug'
    view_url_name = 'djangocms_blog:post-detail'

    def get_object(self, queryset=None):
        try:
            qs = self.model._default_manager.active_translations(**{
                self.slug_field: self.kwargs.get(self.slug_url_kwarg, None)
            }).latest()
        except Post.DoesNotExist:
            raise Http404()
        return qs

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        setattr(self.request, BLOG_CURRENT_POST_IDENTIFIER, self.get_object())
        return context

class PostArchiveView(BaseBlogView, ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = "djangocms_blog/post_list.html"
    date_field = 'date_published'
    allow_empty = True
    allow_future = True
    paginate_by = BLOG_PAGINATION
    view_url_name = 'djangocms_blog:posts-archive'

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
    paginate_by = BLOG_PAGINATION
    view_url_name = 'djangocms_blog:posts-tagged'

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
    paginate_by = BLOG_PAGINATION
    view_url_name = 'djangocms_blog:posts-authors'

    def get_queryset(self):
        qs = super(AuthorEntriesView, self).get_queryset()
        if 'username' in self.kwargs:
            qs = qs.filter(author__username=self.kwargs['username'])
        return qs

    def get_context_data(self, **kwargs):
        kwargs['author'] = User.objects.get(username=self.kwargs.get('username'))
        return super(AuthorEntriesView, self).get_context_data(**kwargs)


class CategoryEntriesView(BaseBlogView, ListView):
    model = Post
    context_object_name = 'post_list'
    template_name = "djangocms_blog/post_list.html"
    _category = None
    paginate_by = BLOG_PAGINATION
    view_url_name = 'djangocms_blog:posts-category'

    @property
    def category(self):
        if not self._category:
            language = get_language()
            self._category = BlogCategory._default_manager.language(language).get(
                translations__language_code=language,
                translations__slug=self.kwargs['category'])
        return self._category

    def get_queryset(self):
        qs = super(CategoryEntriesView, self).get_queryset()
        if 'category' in self.kwargs:
            qs = qs.filter(categories=self.category.pk)
        return qs

    def get_context_data(self, **kwargs):
        kwargs['category'] = self.category
        return super(CategoryEntriesView, self).get_context_data(**kwargs)
