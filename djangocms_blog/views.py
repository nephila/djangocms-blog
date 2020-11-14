import os.path

from aldryn_apphooks_config.mixins import AppConfigMixin
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import get_language
from django.views.generic import DetailView, ListView
from parler.views import TranslatableSlugMixin, ViewUrlMixin

from .models import BlogCategory, Post
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
        return qs.select_related("app_config").prefetch_related(
            "translations", "categories", "categories__translations", "categories__app_config"
        )

    def get_view_url(self):
        if not self.view_url_name:
            raise ImproperlyConfigured("Missing `view_url_name` attribute on {}".format(self.__class__.__name__))

        url = reverse(self.view_url_name, args=self.args, kwargs=self.kwargs, current_app=self.namespace)
        return self.request.build_absolute_uri(url)

    def get_queryset(self):
        language = get_language()
        queryset = self.model._default_manager.namespace(self.namespace).active_translations(language_code=language)
        if not getattr(self.request, "toolbar", None) or not self.request.toolbar.edit_mode_active:
            queryset = queryset.published()
        setattr(self.request, get_setting("CURRENT_NAMESPACE"), self.config)
        return self.optimize(queryset.on_site())

    def get_template_names(self):
        template_path = (self.config and self.config.template_prefix) or "djangocms_blog"
        return os.path.join(template_path, self.base_template_name)


class BaseBlogListView(BaseBlogView):
    context_object_name = "post_list"
    base_template_name = "post_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["TRUNCWORDS_COUNT"] = get_setting("POSTS_LIST_TRUNCWORDS_COUNT")
        return context

    def get_paginate_by(self, queryset):
        return (self.config and self.config.paginate_by) or get_setting("PAGINATION")


class PostDetailView(TranslatableSlugMixin, BaseBlogView, DetailView):
    context_object_name = "post"
    base_template_name = "post_detail.html"
    slug_field = "slug"
    view_url_name = "djangocms_blog:post-detail"
    instant_article = False

    def liveblog_enabled(self):
        return self.object.enable_liveblog and apps.is_installed("djangocms_blog.liveblog")

    def get_template_names(self):
        if self.instant_article:
            template_path = (self.config and self.config.template_prefix) or "djangocms_blog"
            return os.path.join(template_path, "post_instant_article.html")
        else:
            return super().get_template_names()

    def get_queryset(self):
        queryset = self.model._default_manager.all()
        if not getattr(self.request, "toolbar", None) or not self.request.toolbar.edit_mode_active:
            queryset = queryset.published()
        return self.optimize(queryset)

    def get(self, *args, **kwargs):
        # submit object to cms to get corrent language switcher and selected category behavior
        if hasattr(self.request, "toolbar"):
            self.request.toolbar.set_object(self.get_object())
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta"] = self.get_object().as_meta()
        context["instant_article"] = self.instant_article
        context["use_placeholder"] = get_setting("USE_PLACEHOLDER")
        setattr(self.request, get_setting("CURRENT_POST_IDENTIFIER"), self.get_object())
        return context


class PostListView(BaseBlogListView, ListView):
    view_url_name = "djangocms_blog:posts-latest"


class PostArchiveView(BaseBlogListView, ListView):
    date_field = "date_published"
    allow_empty = True
    allow_future = True
    view_url_name = "djangocms_blog:posts-archive"

    def get_queryset(self):
        qs = super().get_queryset()
        if "month" in self.kwargs:
            qs = qs.filter(**{"%s__month" % self.date_field: self.kwargs["month"]})
        if "year" in self.kwargs:
            qs = qs.filter(**{"%s__year" % self.date_field: self.kwargs["year"]})
        return self.optimize(qs)

    def get_context_data(self, **kwargs):
        kwargs["month"] = int(self.kwargs.get("month")) if "month" in self.kwargs else None
        kwargs["year"] = int(self.kwargs.get("year")) if "year" in self.kwargs else None
        if kwargs["year"]:
            kwargs["archive_date"] = now().replace(kwargs["year"], kwargs["month"] or 1, 1)
        context = super().get_context_data(**kwargs)
        return context


class TaggedListView(BaseBlogListView, ListView):
    view_url_name = "djangocms_blog:posts-tagged"

    def get_queryset(self):
        qs = super().get_queryset()
        return self.optimize(qs.filter(tags__slug=self.kwargs["tag"]))

    def get_context_data(self, **kwargs):
        kwargs["tagged_entries"] = self.kwargs.get("tag") if "tag" in self.kwargs else None
        context = super().get_context_data(**kwargs)
        return context


class AuthorEntriesView(BaseBlogListView, ListView):
    view_url_name = "djangocms_blog:posts-author"

    def get_queryset(self):
        qs = super().get_queryset()
        if "username" in self.kwargs:
            qs = qs.filter(**{"author__%s" % User.USERNAME_FIELD: self.kwargs["username"]})
        return self.optimize(qs)

    def get_context_data(self, **kwargs):
        kwargs["author"] = get_object_or_404(User, **{User.USERNAME_FIELD: self.kwargs.get("username")})
        context = super().get_context_data(**kwargs)
        return context


class CategoryEntriesView(BaseBlogListView, ListView):
    _category = None
    view_url_name = "djangocms_blog:posts-category"

    @property
    def category(self):
        if not self._category:
            try:
                self._category = BlogCategory.objects.active_translations(
                    get_language(), slug=self.kwargs["category"]
                ).get()
            except BlogCategory.DoesNotExist:
                raise Http404
        return self._category

    def get(self, *args, **kwargs):
        # submit object to cms toolbar to get correct language switcher behavior
        if hasattr(self.request, "toolbar"):
            self.request.toolbar.set_object(self.category)
        return super().get(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        if "category" in self.kwargs:
            qs = qs.filter(categories=self.category.pk)
        return self.optimize(qs)

    def get_context_data(self, **kwargs):
        kwargs["category"] = self.category
        context = super().get_context_data(**kwargs)
        context["meta"] = self.category.as_meta()
        return context
