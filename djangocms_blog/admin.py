import json
from copy import deepcopy

from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from cms.admin.placeholderadmin import FrontendEditableAdminMixin, PlaceholderAdminMixin
from cms.models import CMSPlugin, ValidationError
from cms.toolbar.utils import get_object_preview_url
from cms.utils import get_language_from_request
from cms.utils.i18n import get_language_tuple, is_valid_site_language, get_language_list
from cms.utils.urlutils import admin_reverse, static_with_version
from django.apps import apps
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Prefetch, signals
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, path, reverse
from django.utils.html import format_html_join
from django.utils.http import urlencode
from django.utils.translation import get_language, gettext_lazy as _, ngettext as __
from parler.admin import TranslatableAdmin

from djangocms_blog.forms import PostAdminForm

from .cms_appconfig import BlogConfig
from .forms import CategoryAdminForm, PostAdminForm
from .models import BlogCategory, Post, PostContent
from .settings import get_setting
from .utils import is_versioning_enabled

signal_dict = {}


def register_extension(klass):
    if issubclass(klass, InlineModelAdmin):
        PostAdmin.inlines = type(PostAdmin.inlines)([klass]) + PostAdmin.inlines
        return
    if issubclass(klass, models.Model):
        if klass in signal_dict:
            raise Exception(f"Can not register {klass} twice.")
        signal_dict[klass] = create_post_post_save(klass)
        signals.post_save.connect(signal_dict[klass], sender=Post, weak=False)
        return
    raise Exception(f"Can not register {klass} type. You can only register a Model or a TabularInline.")


def unregister_extension(klass):
    if issubclass(klass, InlineModelAdmin):
        PostAdmin.inlines.remove(klass)
        return
    if issubclass(klass, models.Model):
        if klass not in signal_dict:
            raise Exception(f"Can not unregister {klass}. No signal found for this class.")
        signals.post_save.disconnect(signal_dict[klass], sender=Post)
        del signal_dict[klass]
        return
    raise Exception(f"Can not unregister {klass} type. You can only unregister a Model or a TabularInline.")


def create_post_post_save(model):
    """A wrapper for creating create_instance function for a specific model."""

    def create_instance(sender, instance, created, **kwargs):
        """Create Model instance for every new Post."""
        if created:
            model.objects.create(post=instance)

    return create_instance


class SiteListFilter(admin.SimpleListFilter):
    title = _("site")
    parameter_name = "sites"

    def lookups(self, request, model_admin):
        restricted_sites = model_admin.get_restricted_sites(request).values_list("id", flat=True)

        qs = Site.objects.all()
        if restricted_sites:
            qs = qs.filter(id__in=restricted_sites)

        return [(site.id, str(site.name)) for site in qs]

    def queryset(self, request, queryset):
        try:
            if "sites" in self.used_parameters:
                return queryset.on_site(Site.objects.get(pk=self.used_parameters["sites"]))
            return queryset
        except Site.DoesNotExist as e:  # pragma: no cover
            raise admin.options.IncorrectLookupParameters(e)
        except ValidationError as e:  # pragma: no cover
            raise admin.options.IncorrectLookupParameters(e)


@admin.register(BlogCategory)
class BlogCategoryAdmin(FrontendEditableAdminMixin, ModelAppHookConfig, TranslatableAdmin):
    form = CategoryAdminForm
    list_display = [
        "name",
        "parent",
        "app_config",
        "all_languages_column",
        "priority",
    ]
    fieldsets = (
        (None, {
            "fields": ("parent", "app_config", "name", "meta_description")
        }),
        (
            _("Info"),
            {
                "fields": ("abstract", "priority",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Images"),
            {
                "fields": ("main_image", "main_image_thumbnail", "main_image_full"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_prepopulated_fields(self, request, obj=None):
        app_config_default = self._app_config_select(request, obj)
        if app_config_default is None and request.method == "GET":
            return {}
        return {"slug": ("name",)}

    class Media:
        css = {"all": ("{}djangocms_blog/css/{}".format(settings.STATIC_URL, "djangocms_blog_admin.css"),)}


class LanguageFilter(admin.SimpleListFilter):
    parameter_name = "language"
    title = _("language")

    def lookups(self, request, model_admin):
        return get_language_tuple()

    def queryset(self, request, queryset):
        return queryset

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }


@admin.register(Post)
class PostAdmin(PlaceholderAdminMixin, FrontendEditableAdminMixin, ModelAppHookConfig, admin.ModelAdmin):
    form = PostAdminForm
    inlines = []
    list_display = ["title", "author",  "app_config", "date_published", "featured"]
    list_display_links = None
    search_fields = ("postcontent"),
    readonly_fields = ("date_created", "date_modified")
    date_hierarchy = "date_published"
    # raw_id_fields = ["author"]
    frontend_editable_fields = ("title", "abstract", "post_text")
    enhance_exclude = ("main_image", "tags")
    actions = [
        "enable_comments",
        "disable_comments",
    ]

    if apps.is_installed("djangocms_blog.liveblog"):
        actions += ["enable_liveblog", "disable_liveblog"]

    _fieldsets = [
        (None, {"fields": [ ["title"], ["subtitle"], ["slug"], ["categories", "app_config"], "language"]}),
         # left empty for sites, author and related fields
        (None, {"fields": [[]]}),
        (
            _("Info"),
            {
                "fields": ["tags", ["date_published", "date_published_end", "date_featured"], ["enable_comments"]],
                "classes": ("collapse",),
            },
        ),
        (
            _("Images"),
            {"fields": [["main_image", "main_image_thumbnail", "main_image_full"]], "classes": ("collapse",)},
        ),
        (
            _("SEO"),
            {
                "fields": ["meta_title", "meta_keywords", "meta_description"],
                "classes": ("collapse",),
            }
        ),
        (None, {"fields": (("date_created", "date_modified"),)})
    ]
    """
    Default fieldsets structure.

    Follow the normal Django fieldsets syntax.

    When customizing the structure, check the :py:attr:`_fieldset_extra_fields_position` to ensure extra fields
    position matches.
    """
    _fieldset_extra_fields_position = {
        "abstract": (0, 1),
        "post_text": (0, 1),
        "sites": (1, 1, 0),
        "author": (1, 1, 0),
        "enable_liveblog": (2, 1, 2),
        "related": (1, 1, 0),
    }
    """
    Indexes where to append extra fields.

    Key: Supported extra / optional field name
    Value: None / 2 / 3 item tuple. If you want to hide the field in any case set ``None`` as dictionary value,
    otherwise use a tuple containing the index of the the "fields" attribute of the selected fieldset row and
    an optional third value if the target "fields" has subgroups.
    """

    app_config_values = {"default_published": "publish"}
    _sites = None
    _post_content_type = None
    _language_cache = {}

    def get_language(self):
        return get_language()

    def get_language_selector(self):
        return get_language_tuple()

    def get_changelist_instance(self, request):
        """Set language property and remove language from changelist_filter_params"""
        if request.method == "GET":
            request.GET = request.GET.copy()
            self.language = request.GET.pop("language", [self.get_language()])[0]
            if self.language not in get_language_list():
                self.language = self.get_language()
            self._content_cache = {}  # Language-specific cache needs to be cleared when language is changed
        instance = super().get_changelist_instance(request)
        if request.method == "GET" and "language" in instance.params:
            del instance.params["language"]
        return instance

    def get_list_display(self, request):
        return (*self.list_display, *self._get_status_indicator(request), self._get_actions(request),)

    def get_content_obj_for_grouper(self, obj):
        """Get latest postcontent object for post and cache it."""
        if not obj in self._content_cache:
            self._content_cache[obj] = obj.postcontent_set(manager="admin_manager")\
                .filter(language=self.language)\
                .latest_content()\
                .first()
        return self._content_cache[obj]

    def title(self, obj):
        content_obj = self.get_content_obj_for_grouper(obj)
        if content_obj:
            return content_obj.title
        return _("Empty")

    def get_search_results(self, request, queryset, search_term):
        # qs, distinct = super().get_search_results(request, queryset, search_term)
        content_title = PostContent.admin_manager.filter(title__icontains=search_term).values("post_id").latest_content()
        return queryset.filter(pk__in=content_title), True

    def _get_actions(self, request):
        def view_action(obj):
            content_obj = self.get_content_obj_for_grouper(obj)
            view_url = self.endpoint_url("cms_placeholder_render_object_preview", content_obj) if content_obj else None
            edit_url = f'{reverse("admin:djangocms_blog_post_change", args=(obj.pk,))}' \
                       f'?{urlencode(dict(language=self.language))}'
            return format_html_join(
                "",
                "{}",
                (
                    (render_to_string(
                        "djangocms_blog/admin/icons.html",
                        {
                            "url": view_url or "",
                            "icon": "view",
                            "action": "get",
                            "disabled": not view_url,
                            "target": "_top",
                            "title": _("View") if view_url else "",
                        }
                    ),),
                    (render_to_string(
                        "djangocms_blog/admin/icons.html",
                        {
                            "url": edit_url,
                            "icon": "settings" if content_obj else "plus",
                            "action": "get",
                            "title": _("Post settings") if view_url else _("Add language"),
                        }
                    ),),
                )
            )

        view_action.short_description = _("Actions")
        return view_action

    def _get_status_indicator(self, request):
        """Gets the status indicator action if djangocms_versioning is enabled"""
        if is_versioning_enabled():
            from djangocms_versioning.indicators import (
                content_indicator,
                content_indicator_menu,
                indicator_description,
            )

            def indicator(obj):
                post_content = self.get_content_obj_for_grouper(obj)

                status = content_indicator(post_content)
                menu = content_indicator_menu(request, status, post_content._version) if status else None
                return render_to_string(
                    "admin/djangocms_versioning/indicator.html",
                    {
                        "state": status or "empty",
                        "description": indicator_description.get(status, _("Empty")),
                        "menu_template": "admin/cms/page/tree/indicator_menu.html",
                        "menu": json.dumps(render_to_string("admin/cms/page/tree/indicator_menu.html",
                                                          dict(indicator_menu_items=menu))) if menu else None,
                    }
                )
            indicator.short_description = _("Status")
            return indicator,  # Must be interable of length one
        return ()

    @staticmethod
    def endpoint_url(admin, obj):
        if PostAdmin._post_content_type is None:
            # Use class as cache
            from django.contrib.contenttypes.models import ContentType

            PostAdmin._post_content_type = ContentType.objects.get_for_model(obj.__class__).pk
        try:
            return admin_reverse(admin, args=[PostAdmin._post_content_type, obj.pk])
        except NoReverseMatch:
            return ""

    def get_form(self, request, obj=None, **kwargs):
        """Adds the language from the request to the form class"""
        form_class = super().get_form(request, obj, **kwargs)
        form_class.language = get_language_from_request(request)
        return form_class

    def get_extra_context(self, request, object_id=None):
        """Provide the language to edit"""
        language = get_language_from_request(request)
        if object_id:
            # Instance provided? Get corresponding postconent
            instance = get_object_or_404(self.model, pk=object_id)
            qs = instance.postcontent_set(manager="admin_manager")
            filled_languages = qs.values_list("language", flat=True).distinct()
            content_instance = qs.filter(language=language).latest_content().first()
        else:
            content_instance = None
            filled_languages = []

        context = {
            "language_tabs": get_language_tuple(),
            "changed_message": _("Content for the current language has been changed. Click \"Cancel\" to "
                                 "return to the form and save changes. Click \"OK\" to discard changes."),
            "language": language,
            "filled_language": filled_languages,
            "content_instance": content_instance,
        }
        return context

    def get_preserved_filters(self, request):
        """Always preserve language get parameter!"""
        preserved_filters = super().get_preserved_filters(request)
        if "_changelist_filters" in preserved_filters:
            # changelist needs to add filters to _changelist_filters
            preserved_filters += f"%26language%3D{self.language}"
        elif request.GET.get("language", None)  and "language=" not in preserved_filters:
            # change and add views
            preserved_filters += "&language=" + request.GET.get("language")
        print(f"{preserved_filters=}")
        return preserved_filters

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return super().change_view(request, object_id, form_url, {
            **(extra_context or {}),
            **self.get_extra_context(request, object_id),
        })

    def add_view(self, request, form_url='', extra_context=None):
        return super().add_view(request, form_url, {
            **(extra_context or {}),
            **self.get_extra_context(request, None),
        })

    @admin.action(
        description=_("Enable comments for selection")
    )
    def enable_comments(self, request, queryset):
        """
        Bulk action to enable comments for selected posts.
        queryset must not be empty (ensured by django CMS).
        """
        updates = queryset.filter(enable_comments=False).update(enable_comments=True)
        messages.add_message(
            request,
            messages.INFO,
            __("Comments for %(updates)d entry enabled.", "Comments for %(updates)d entries enabled", updates)
            % {"updates": updates},
        )

    @admin.action(
        description=_("Disable comments for selection ")
    )
    def disable_comments(self, request, queryset):
        """
        Bulk action to disable comments for selected posts.
        queryset must not be empty (ensured by django CMS).
        """
        updates = queryset.filter(enable_comments=True).update(enable_comments=False)
        messages.add_message(
            request,
            messages.INFO,
            __("Comments for %(updates)d entry disabled.", "Comments for %(updates)d entries disabled.", updates)
            % {"updates": updates},
        )

    @admin.action(
        description=_("Enable liveblog for selection")
    )
    def enable_liveblog(self, request, queryset):
        """
        Bulk action to enable comments for selected posts.
        queryset must not be empty (ensured by django CMS).
        """
        updates = queryset.filter(enable_liveblog=False).update(enable_liveblog=True)
        messages.add_message(
            request,
            messages.INFO,
            __("Liveblog for %(updates)d entry enabled.", "Liveblog for %(updates)d entries enabled.", updates)
            % {"updates": updates},
        )

    @admin.action(
        description=_("Disable liveblog for selection ")
    )
    def disable_liveblog(self, request, queryset):
        """
        Bulk action to disable comments for selected posts.
        queryset must not be empty (ensured by django CMS).
        """
        updates = queryset.filter(enable_liveblog=True).update(enable_liveblog=False)
        messages.add_message(
            request,
            messages.INFO,
            __("Liveblog for %(updates)d entry enabled.", "Liveblog for %(updates)d entries enabled.")
            % {"updates": updates},
        )

    # Make bulk action menu entries localizable

    def get_list_filter(self, request):
        filters = ["categories", "app_config", ]
        if get_setting("MULTISITE"):
            filters.append(SiteListFilter)
        try:
            from taggit_helpers.admin import TaggitListFilter

            filters.append(TaggitListFilter)
        except ImportError:  # pragma: no cover
            try:
                from taggit_helpers import TaggitListFilter

                filters.append(TaggitListFilter)
            except ImportError:
                pass
        return filters

    def lookup_allowed(self, lookup, value):
        return super().lookup_allowed(lookup,value) or any((
            lookup.startswith("post__categories"),
            lookup.startswith("post__app_config"),
        ))

    # def get_urls(self):
    #     """
    #     Customize the modeladmin urls
    #     """
    #     urls = [
    #         path(
    #             "publish/<int:pk>/",
    #             self.admin_site.admin_view(self.publish_post),
    #             name="djangocms_blog_publish_article",
    #         ),
    #     ]
    #     urls.extend(super().get_urls())
    #     return urls

    # def post_add_plugin(self, request, obj1, obj2=None):
    #     if isinstance(obj1, CMSPlugin):
    #         plugin = obj1
    #     elif isinstance(obj2, CMSPlugin):
    #         plugin = obj2
    #     if plugin.plugin_type in get_setting("LIVEBLOG_PLUGINS"):
    #         plugin = plugin.move(plugin.get_siblings().first(), "first-sibling")
    #     if isinstance(obj1, CMSPlugin):
    #         return super().post_add_plugin(request, plugin)
    #     elif isinstance(obj2, CMSPlugin):
    #         return super().post_add_plugin(request, obj1, plugin)

    # def publish_post(self, request, pk):
    #     """
    #     Admin view to publish a single post
    #
    #     :param request: request
    #     :param pk: primary key of the post to publish
    #     :return: Redirect to the post itself (if found) or fallback urls
    #     """
    #     language = get_language_from_request(request, check_path=True)
    #     try:
    #         post = Post.objects.get(pk=int(pk))
    #         post.publish = True
    #         post.save()
    #         return HttpResponseRedirect(post.get_absolute_url(language))
    #     except Exception:
    #         try:
    #             return HttpResponseRedirect(request.headers["referer"])
    #         except KeyError:
    #             return HttpResponseRedirect(reverse("djangocms_blog:posts-latest"))

    def has_restricted_sites(self, request):
        """
        Whether the current user has permission on one site only

        :param request: current request
        :return: boolean: user has permission on only one site
        """
        sites = self.get_restricted_sites(request)
        return sites and sites.count() == 1

    def get_restricted_sites(self, request):
        """
        The sites on which the user has permission on.

        To return the permissions, the method check for the ``get_sites``
        method on the user instance (e.g.: ``return request.user.get_sites()``)
        which must return the queryset of enabled sites.
        If the attribute does not exists, the user is considered enabled
        for all the websites.

        :param request: current request
        :return: boolean or a queryset of available sites
        """
        try:
            return request.user.get_sites()
        except AttributeError:  # pragma: no cover
            return Site.objects.none()

    def _set_config_defaults(self, request, form, obj=None):
        form = super()._set_config_defaults(request, form, obj)
        sites = self.get_restricted_sites(request)
        if "sites" in form.base_fields and sites.exists():
            form.base_fields["sites"].queryset = self.get_restricted_sites(request).all()
        return form

    def _get_available_posts(self, config):
        if config:
            return self.model.objects.filter(app_config__namespace=config.namespace).all()
        return []

    def get_fieldsets(self, request, obj=None):
        """
        Customize the fieldsets according to the app settings

        :param request: request
        :param obj: post
        :return: fieldsets configuration
        """
        app_config_default = self._app_config_select(request, obj)
        if app_config_default is None and request.method == "GET":
            return super().get_fieldsets(request, obj)
        if not obj:
            config = app_config_default
        else:
            config = obj.app_config

        fsets = deepcopy(self._fieldsets)
        related_posts = []
        abstract = bool(getattr(config, "use_abstract", get_setting("USE_ABSTRACT")))
        placeholder = bool(getattr(config, "use_placeholder", get_setting("USE_PLACEHOLDER")))
        related = getattr(config, "use_related", get_setting("USE_RELATED"))
        related = bool(int(related)) if isinstance(related, str) and related.isnumeric() else bool(related)
        if related:
            related_posts = self._get_available_posts(config)
        if abstract:
            # self._patch_fieldsets(fsets, "abstract")
            pass
        if not placeholder:
            self._patch_fieldsets(fsets, "post_text")
        if get_setting("MULTISITE") and not self.has_restricted_sites(request):
            # self._patch_fieldsets(fsets, "sites")
            pass
        if request.user.is_superuser:
            self._patch_fieldsets(fsets, "author")
        if apps.is_installed("djangocms_blog.liveblog"):
            self._patch_fieldsets(fsets, "enable_liveblog")
        filter_function = get_setting("ADMIN_POST_FIELDSET_FILTER")
        if related_posts:
            self._patch_fieldsets(fsets, "related")
        if callable(filter_function):
            fsets = filter_function(fsets, request, obj=obj)
        return fsets

    def _patch_fieldsets(self, fsets, field):
        """Patch the fieldsets list with additional fields, based on :py:attr:`_fieldset_extra_fields_position`."""
        positions = self._get_extra_field_position(field)
        if not positions or len(positions) not in (2, 3) or not all(True for i in positions[:2] if i is not None):
            return fsets
        if len(positions) == 2 or positions[2] is None:
            fsets[positions[0]][positions[1]]["fields"].append(field)
        elif len(positions) == 3:
            fsets[positions[0]][positions[1]]["fields"][positions[2]].append(field)
        return fsets

    def _get_extra_field_position(self, field):
        """Return the position in the fieldset where to add the given field."""
        return self._fieldset_extra_fields_position.get(field, (None, None, None))

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj or form.instance, form, change)
        content_dict = {
            field: form.cleaned_data[field] for field in form._postcontent_fields
        }
        if form.content_instance is None or form.content_instance.pk is None:
            PostContent.objects.with_user(request.user).create(
                post=form.instance,
                language=form.language,
                **content_dict,
            )
        else:
            print(f"   Updating content for {form.language=}")
            for key, value in content_dict.items():
                setattr(form.content_instance, key, value)
            form.content_instance.save()
        # obj.post._set_default_author(request.user)
        # obj.post.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        sites = self.get_restricted_sites(request)
        if sites.exists():
            pks = list(sites.all().values_list("pk", flat=True))
            qs = qs.filter(sites__in=pks)
        return qs.distinct().prefetch_related(Prefetch('postcontent_set', queryset=PostContent.admin_manager.all()))

    def save_related(self, request, form, formsets, change):
        if self.get_restricted_sites(request).exists():
            if "sites" in form.cleaned_data:
                form_sites = form.cleaned_data.get("sites", [])
                removed = set(self.get_restricted_sites(request).all()).difference(form_sites)
                diff_original = set(form.instance.sites.all()).difference(removed).union(form_sites)
                form.cleaned_data["sites"] = diff_original
            else:
                form.instance.sites.add(*self.get_restricted_sites(request).all().values_list("pk", flat=True))
        super().save_related(request, form, formsets, change)

    def view_on_site(self, obj):
        return get_object_preview_url(obj)

    class Media:
        js = ("admin/js/jquery.init.js", "djangocms_versioning/js/indicators.js", "djangocms_blog/js/language-selector.js")
        css = {"all": ("{}djangocms_blog/css/{}".format(settings.STATIC_URL, "djangocms_blog_admin.css"),
                       static_with_version("cms/css/cms.pagetree.css"),
                       "djangocms_versioning/css/actions.css",
                       )}


@admin.register(BlogConfig)
class BlogConfigAdmin(BaseAppHookConfig, TranslatableAdmin):
    @property
    def declared_fieldsets(self):
        return self.get_fieldsets(None)

    def get_fieldsets(self, request, obj=None):
        """
        Fieldsets configuration
        """
        return [
            (None, {"fields": ("type", "namespace", "app_title", "object_name")}),
            (
                _("Generic"),
                {
                    "fields": (
                        "config.default_published",
                        "config.use_placeholder",
                        "config.use_abstract",
                        "config.set_author",
                        "config.use_related",
                    )
                },
            ),
            (
                _("Layout"),
                {
                    "fields": (
                        "config.urlconf",
                        "config.paginate_by",
                        "config.url_patterns",
                        "config.template_prefix",
                        "config.menu_structure",
                        "config.menu_empty_categories",
                        ("config.default_image_full", "config.default_image_thumbnail"),
                    ),
                    "classes": ("collapse",),
                },
            ),
            (
                _("Notifications"),
                {"fields": ("config.send_knock_create", "config.send_knock_update"), "classes": ("collapse",)},
            ),
            (
                _("Sitemap"),
                {
                    "fields": (
                        "config.sitemap_changefreq",
                        "config.sitemap_priority",
                    ),
                    "classes": ("collapse",),
                },
            ),
            (_("Meta"), {"fields": ("config.object_type",)}),
            (
                "Open Graph",
                {
                    "fields": (
                        "config.og_type",
                        "config.og_app_id",
                        "config.og_profile_id",
                        "config.og_publisher",
                        "config.og_author_url",
                        "config.og_author",
                    ),
                    "description": _("You can provide plain strings, Post model attribute or method names"),
                },
            ),
            (
                "Twitter",
                {
                    "fields": (
                        "config.twitter_type",
                        "config.twitter_site",
                        "config.twitter_author",
                    ),
                    "description": _("You can provide plain strings, Post model attribute or method names"),
                },
            ),
            (
                "Schema.org",
                {
                    "fields": (
                        "config.gplus_type",
                        "config.gplus_author",
                    ),
                    "description": _("You can provide plain strings, Post model attribute or method names"),
                },
            ),
        ]

    def save_model(self, request, obj, form, change):
        """
        Clear menu cache when changing menu structure
        """
        if "config.menu_structure" in form.changed_data:
            from menus.menu_pool import menu_pool

            menu_pool.clear(all=True)
        """
        Reload urls when changing url config
        """
        if "config.urlconf" in form.changed_data:
            from cms.signals.apphook import trigger_restart
            trigger_restart()
        return super().save_model(request, obj, form, change)


