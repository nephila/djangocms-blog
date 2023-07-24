import os.path

from cms.apphook_pool import apphook_pool
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, resolve, Resolver404
from django.utils.timezone import now
from django.utils.translation import get_language, get_language_from_request, override
from django.views.generic import DetailView, ListView
from parler.views import TranslatableSlugMixin, ViewUrlMixin

from .cms_appconfig import get_app_instance
from .models import BlogCategory, Post, PostContent
from .settings import get_setting

User = get_user_model()


class BlogConfigMixin:
    def dispatch(self, request, *args, **kwargs):
        """Detect current namespace and config instance. Add both to the view object and
        make namespace avilable to the request."""

        self.namespace, self.config = get_app_instance(request)
        request.current_app = self.namespace
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        """Make current app available to the template"""
        if "current_app" in response_kwargs:  # pragma: no cover
            response_kwargs["current_app"] = self.namespace
        return super().render_to_response(context, **response_kwargs)


class PostDetailView(BlogConfigMixin, DetailView):
    model = PostContent
    context_object_name = "post_content"
    base_template_name = "post_detail.html"
    slug_field = "slug"
    view_url_name = "djangocms_blog:post-detail"
    instant_article = False

    def get(self, request, *args, **kwargs):
        """Make toolbar object's apphook config available"""
        if hasattr(request, "toolbar") and self.config is None:
            self.config = getattr(request.toolbar.get_object().post, "app_config", None)
        return super().get(request, *args, **kwargs)

    def liveblog_enabled(self):
        return self.object.post.enable_liveblog and apps.is_installed("djangocms_blog.liveblog")

    def get_template_names(self):
        if self.instant_article:
            template_path = (self.config and self.config.template_prefix) or "djangocms_blog"
            return os.path.join(template_path, "post_instant_article.html")
        else:
            template_path = (self.config and self.config.template_prefix) or "djangocms_blog"
            return os.path.join(template_path, self.base_template_name)

    def get_object(self):
        obj = super().get_object()
        try:
            # Add to toolbar if not in endpoint
            self.request.toolbar.set_object(obj)
        except AttributeError:
            pass
        setattr(self.request, get_setting("CURRENT_POST_IDENTIFIER"), obj)
        return obj

    def get_context_data(self, **kwargs):
        setattr(self.request, get_setting("CURRENT_NAMESPACE"), self.config)
        context = super().get_context_data(**kwargs)
        context["post"] = context["post_content"]  # Temporary to allow for easier transition from v3 to v4
        context["meta"] = self.get_object().as_meta()
        context["instant_article"] = self.instant_article
        context["use_placeholder"] = get_setting("USE_PLACEHOLDER")
        return context


class ToolbarDetailView(PostDetailView):
    """Mimics DetailView but takes content object from render function"""
    def get_object(self):
        content_object = self.args[0]
        self.request.current_app = content_object.post.app_config.namespace
        setattr(self.request, get_setting("CURRENT_NAMESPACE"), content_object.post.app_config)
        return content_object


class BaseConfigListViewMixin(BlogConfigMixin):
    def optimize(self, qs):
        """
        Apply select_related / prefetch_related to optimize the view queries
        :param qs: queryset to optimize
        :return: optimized queryset
        """
        return qs.select_related("post__app_config").prefetch_related(
            "post__categories", "post__categories__translations", "post__categories__app_config"
        )

    def get_view_url(self):
        if not self.view_url_name:
            raise ImproperlyConfigured(f"Missing `view_url_name` attribute on {self.__class__.__name__}")

        url = reverse(self.view_url_name, args=self.args, kwargs=self.kwargs, current_app=self.namespace)
        return self.request.build_absolute_uri(url)

    def get_queryset(self):
        language = get_language()
        if hasattr(self.request, "toolbar") and (self.request.toolbar.edit_mode_active or self.request.toolbar.preview_mode_active):
            queryset = self.model.admin_manager.latest_content()
        else:
            queryset = self.model.objects.all()
        queryset = queryset.filter(language=language, post__app_config__namespace=self.namespace)
        setattr(self.request, get_setting("CURRENT_NAMESPACE"), self.config)
        return self.optimize(queryset.on_site())

    def get_template_names(self):
        template_path = (self.config and self.config.template_prefix) or "djangocms_blog"
        return os.path.join(template_path, self.base_template_name)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["TRUNCWORDS_COUNT"] = get_setting("POSTS_LIST_TRUNCWORDS_COUNT")
        return context

    def get_paginate_by(self, queryset):
        return (self.config and self.config.paginate_by) or get_setting("PAGINATION")


class PostListView(BaseConfigListViewMixin, ListView):
    model = PostContent
    base_template_name = "post_list.html"
    view_url_name = "djangocms_blog:posts-latest"


class CategoryListView(BlogConfigMixin, ViewUrlMixin, TranslatableSlugMixin, ListView):
    model = BlogCategory
    context_object_name = "category_list"
    base_template_name = "category_list.html"
    view_url_name = "djangocms_blog:categories-all"

    def get_queryset(self):
        language = get_language()
        queryset = self.model._default_manager\
            .filter(app_config__namespace=self.namespace)\
            .active_translations(language_code=language)
        queryset = queryset.filter(parent__isnull=True, priority__isnull=False)  # Only top-level categories
        setattr(self.request, get_setting("CURRENT_NAMESPACE"), self.config)
        return queryset

    def get_template_names(self):
        template_path = (self.config and self.config.template_prefix) or "djangocms_blog"
        return os.path.join(template_path, self.base_template_name)


class PostArchiveView(BaseConfigListViewMixin, ListView):
    model = PostContent
    context_object_name = "post_list"
    base_template_name = "post_list.html"
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


class TaggedListView(BaseConfigListViewMixin, ListView):
    model = PostContent
    context_object_name = "post_list"
    base_template_name = "post_list.html"
    view_url_name = "djangocms_blog:posts-tagged"

    def get_queryset(self):
        qs = super().get_queryset()
        return self.optimize(qs.filter(tags__slug=self.kwargs["tag"]))

    def get_context_data(self, **kwargs):
        kwargs["tagged_entries"] = self.kwargs.get("tag") if "tag" in self.kwargs else None
        context = super().get_context_data(**kwargs)
        return context


class AuthorEntriesView(BaseConfigListViewMixin, ListView):
    model = PostContent
    context_object_name = "post_list"
    base_template_name = "post_list.html"
    view_url_name = "djangocms_blog:posts-author"

    def get_queryset(self):
        qs = super().get_queryset()
        if "username" in self.kwargs:
            qs = qs.filter(**{"post__author__%s" % User.USERNAME_FIELD: self.kwargs["username"]})
        return self.optimize(qs)

    def get_context_data(self, **kwargs):
        kwargs["author"] = get_object_or_404(User, **{User.USERNAME_FIELD: self.kwargs.get("username")})
        context = super().get_context_data(**kwargs)
        return context


class CategoryEntriesView(BaseConfigListViewMixin, ListView):
    _category = None
    model = PostContent
    context_object_name = "post_list"
    base_template_name = "post_list.html"
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
