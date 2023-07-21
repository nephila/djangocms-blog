import copy
from copy import deepcopy

from cms.admin.placeholderadmin import FrontendEditableAdminMixin, PlaceholderAdminMixin
from cms.models import CMSPlugin, ValidationError
from cms.toolbar.utils import get_object_preview_url
from cms.utils import get_language_from_request
from cms.utils.i18n import get_language_list, get_language_tuple, is_valid_site_language
from cms.utils.urlutils import admin_reverse, static_with_version
from django.apps import apps
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Prefetch, signals
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, path, reverse
from django.utils.html import format_html_join
from django.utils.http import urlencode
from django.utils.translation import get_language, gettext_lazy as _, ngettext as __
from django.views.generic import RedirectView
from parler.admin import TranslatableAdmin


from .forms import CategoryAdminForm, PostAdminForm
from .models import BlogConfig, BlogCategory, Post, PostContent
from .settings import get_setting
from .utils import is_versioning_enabled

signal_dict = {}

if is_versioning_enabled():
    from djangocms_versioning.admin import StateIndicatorMixin
else:
    # Declare stubs
    class StateIndicatorMixin:
        def state_indicator(self, obj):
            pass

        def get_list_display(self, request):
            # remove "indicator" entry
            return [item for item in super().get_list_display(request) if item != "indicator"]


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


def admin_get_object_or_404(model, **kwargs):
    try:
        return model.admin_manager.get(**kwargs)
    except ObjectDoesNotExist:
        raise Http404


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


class ModelAppHookConfig:
    app_config_selection_title = _("Select app config")
    app_config_selection_desc = _("Select the app config for the new object")
    app_config_values = {}

    def _app_config_select(self, request, obj):
        """
        Return the select value for apphook configs

        :param request: request object
        :param obj: current object
        :return: False if no preselected value is available (more than one or no apphook
                 config is present), apphook config instance if exactly one apphook
                 config is defined or apphook config defined in the request or in the current
                 object, False otherwise
        """
        if not obj and not request.GET.get("app_config", False):
            if BlogConfig.objects.count() == 1:
                return BlogConfig.objects.first()
            return None
        elif obj and getattr(obj, "app_config", False):
            return getattr(obj, "app_config")
        elif request.GET.get("app_config", False):
            return BlogConfig.objects.get(pk=int(request.GET.get("app_config", False)))
        return False

    def _set_config_defaults(self, request, form, obj=None):
        """
        Cycle through app_config_values and sets the form value according to the
        options in the current apphook config.

        self.app_config_values is a dictionary containing config options as keys, form fields as
        values::

            app_config_values = {
                'apphook_config': 'form_field',
                ...
            }

        :param request: request object
        :param form: model form for the current model
        :param obj: current object
        :return: form with defaults set
        """
        for config_option, field in self.app_config_values.items():
            if field in form.base_fields:
                form.base_fields[field].initial = self.get_config_data(request, obj, config_option)
        return form

    def get_fieldsets(self, request, obj=None):
        """
        If the apphook config must be selected first, returns a fieldset with just the
         app config field and help text
        :param request:
        :param obj:
        :return:
        """
        app_config_default = self._app_config_select(request, obj)
        if app_config_default is None and request.method == "GET":
            return (
                (
                    _(self.app_config_selection_title),
                    {
                        "fields": ("app_config",),
                        "description": _(self.app_config_selection_desc),
                    },
                ),
            )
        else:
            return super().get_fieldsets(request, obj)

    def get_config_data(self, request, obj, name):
        """
        Method that retrieves a configuration option for a specific AppHookConfig instance

        :param request: the request object
        :param obj: the model instance
        :param name: name of the config option as defined in the config form

        :return value: config value or None if no app config is found
        """
        return_value = None
        config = None
        if obj:
            try:
                config = getattr(obj, "app_config", False)
            except ObjectDoesNotExist:  # pragma: no cover
                pass
        if not config and "app_config" in request.GET:
            try:
                config = BlogConfig.objects.get(pk=request.GET["app_config"])
            except BlogConfig.DoesNotExist:  # pragma: no cover
                pass
        if config:
            return_value = getattr(config, name)
        return return_value

    def get_form(self, request, obj=None, **kwargs):
        """
        Provides a flexible way to get the right form according to the context

        For the add view it checks whether the app_config is set; if not, a special form
        to select the namespace is shown, which is reloaded after namespace selection.
        If only one namespace exists, the current is selected and the normal form
        is used.
        """
        form = super().get_form(request, obj, **kwargs)
        if "app_config" not in form.base_fields:
            return form
        app_config_default = self._app_config_select(request, obj)
        if app_config_default:
            form.base_fields["app_config"].initial = app_config_default
            get = copy.copy(request.GET)  # Make a copy to modify
            get["app_config"] = app_config_default.pk
            request.GET = get
        elif app_config_default is None and request.method == "GET":

            class InitialForm(form):
                class Meta(form.Meta):
                    fields = ("app_config",)

            form = InitialForm
        form = self._set_config_defaults(request, form, obj)
        return form


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


# class LanguageFilter(admin.SimpleListFilter):
#     parameter_name = "language"
#     title = _("language")
#
#     def lookups(self, request, model_admin):
#         return get_language_tuple()
#
#     def queryset(self, request, queryset):
#         return queryset
#
#     def choices(self, changelist):
#         for lookup, title in self.lookup_choices:
#             yield {
#                 'selected': self.value() == str(lookup),
#                 'query_string': changelist.get_query_string({self.parameter_name: lookup}),
#                 'display': title,
#             }

class GrouperChangeList(ChangeList):
    """Subclass ChangeList to disregard language get parameter as filter"""
    def get_filters_params(self, params=None):
        lookup_params = super().get_filters_params(params)
        if "language" in lookup_params:
            del lookup_params["language"]
        return lookup_params


class GrouperLanguageAdminMixin:
    """Allows to switch grouper admin view by language"""
    def __init__(self, *args, **kwargs):
        self._content_cache = {}
        super().__init__(*args, **kwargs)

    def get_language(self):
        return get_language()

    def get_language_selector(self):
        return get_language_tuple()

    def get_changelist(self, request, **kwargs):
        """Allow for language as a non-filter parameter"""
        return GrouperChangeList

    def get_changelist_instancex(self, request):
        """
        Return a `ChangeList` instance based on `request`. May raise
        `IncorrectLookupParameters`.
        """
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        # Add the action checkboxes if any actions are available.
        if self.get_actions(request):
            list_display = ["action_checkbox", *list_display]
        sortable_by = self.get_sortable_by(request)
        ChangeList = self.get_changelist(request)
        return ChangeList(
            request,
            self.groupermodel,
            list_display,
            list_display_links,
            self.get_list_filter(request),
            self.date_hierarchy,
            self.get_search_fields(request),
            self.get_list_select_related(request),
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
            sortable_by,
            self.search_help_text,
        )

    def get_language_from_request(self, request):
        if request.method == "GET":
            language = request.GET.get("language", self.get_language())
            if language not in get_language_list():
                language = self.get_language()
            if not hasattr(self, "language") or language != self.language:
                self.language = language
                self._content_cache = {}  # Language-specific cache needs to be cleared when language is changed

    def get_changelist_instance(self, request):
        """Set language property"""
        self.get_language_from_request(request)
        return super().get_changelist_instance(request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Set language property"""
        self.get_language_from_request(request)
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        """Add view with extra context"""
        self.get_language_from_request(request)
        return super().add_view(request, form_url, extra_context)

    def get_content_obj_for_grouper(self, obj):
        """Get the latest content object for post and cache it."""
        if obj is None:
            return None
        if not obj in self._content_cache:
            assert self.language
            self._content_cache[obj] = obj.postcontent_set(manager="admin_manager")\
                .filter(language=self.language)\
                .latest_content()\
                .first()
        return self._content_cache[obj]

    def get_preserved_filters(self, request):
        """Always preserve language get parameter!"""
        preserved_filters = super().get_preserved_filters(request)
        # Language from property (changelist view) or request (change/add view)
        language = self.language if hasattr(self, "langauge") else get_language_from_request(request)
        if "language" not in preserved_filters:
            preserved_filters += f"%26language%3D{language}"
        elif preserved_filters == "":
            preserved_filters = f"_changelist_filters=language%3D{language}"
        return preserved_filters

    def view_on_site(self, obj):
        content_obj = self.get_content_obj_for_grouper(obj)
        return get_object_preview_url(content_obj) if content_obj else None

from cms.admin.utils import GrouperModelAdmin

@admin.register(Post)
class PostAdmin(
    PlaceholderAdminMixin,
    FrontendEditableAdminMixin,
    ModelAppHookConfig,
    GrouperModelAdmin,
):
    form = PostAdminForm
    inlines = []
    list_display = ("title", "author",  "app_config", "state_indicator")
    list_display_links = ("title",)
    search_fields = ("author__first_name",)
    readonly_fields = ("date_created", "date_modified")
    date_hierarchy = "date_published"
    autocomplete_fields = ["author"]
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

    def get_list_display(self, request):
        return (*super().get_list_display(request), self._get_actions(request),)

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
                            "title": _("Preview") if view_url else "",
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

    def get_readonly_fields(self, request, obj=None):
        # First, get read-only fields for grouper
        fields = super().get_readonly_fields(request, obj)
        content_obj = self.get_content_obj_for_grouper(obj)
        if not self.can_change(request, content_obj):
            # Only allow content object fields to be edited if user can change them
            fields += tuple(self.form._meta.labels)  # <= _postcontent_fields
        return fields

    def can_change(self, request, content_obj):
        """Returns True if user can change content_obj"""
        if content_obj and is_versioning_enabled():
            from djangocms_versioning.models import Version

            version = Version.objects.get_for_content(content_obj)
            return version.check_modify.as_bool(request.user)
        return True

    def get_extra_context(self, request, obj=None):
        """Provide the language to edit"""
        language = get_language_from_request(request)
        if obj:  # Instance provided -> change view?
            if isinstance(obj, self.model):  # Grouper?
                instance = obj
                qs = instance.postcontent_set(manager="admin_manager")
                content_instance = qs.filter(language=language).latest_content().first()
            else:  # Content
                content_instance = obj
                instance = content_instance.post
                qs = instance.postcontent_set(manager="admin_manager")
            filled_languages = qs.values_list("language", flat=True).distinct()
            title = _("%(object_name)s Properties") % dict(object_name=instance.app_config.object_name)
        else:
            content_instance = None
            filled_languages = []
            title = _("Add new %(object_name)s") % dict(object_name=Post._meta.verbose_name)

        language_tuple = get_language_tuple()
        extra_context = {
            "language_tabs": language_tuple,
            "changed_message": _("Content for the current language has been changed. Click \"Cancel\" to "
                                 "return to the form and save changes. Click \"OK\" to discard changes."),
            "language": language,
            "filled_language": filled_languages,
            "content_instance": content_instance,
            "title": title,
            "subtitle": content_instance.title if content_instance else _("Add %(language)s") % dict(language=dict(language_tuple).get(language, "")),
        }
        return extra_context

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Change view with extra context"""
        obj = get_object_or_404(self.model, pk=object_id)
        return super().change_view(request, object_id, form_url, {
            **(extra_context or {}),
            **self.get_extra_context(request, obj),
        })

    def change_content_view(self, request, object_id):
        obj = admin_get_object_or_404(PostContent, pk=object_id)
        return self.change_view(
            request,
            str(obj.post.pk),
            form_url="",
            extra_context=self.get_extra_context(request, obj),
        )

    def add_view(self, request, form_url='', extra_context=None):
        """Add view with extra context"""
        return super().add_view(request, form_url, {
            **(extra_context or {}),
            **self.get_extra_context(request, None),
        })

    def add_content_view(self, request):
        raise NotImplementedError
        return self.add_view(request, form_url="", extra_context=self.get_extra_context(request, None))


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

    def get_urls(self):
        """
        Customize the modeladmin urls
        """
        urls = [
            path(
                "add_content/",
                self.admin_site.admin_view(self.add_content_view),
                name="djangocms_blog_postcontent_add",
            ),
            path(
                "content/<object_id>/",
                self.admin_site.admin_view(self.change_content_view),
                name="djangocms_blog_postcontent_change",
            ),
            path(
                "content/",
                RedirectView.as_view(pattern_name="djangocms_blog_post_changelist"),
                name="djangocms_blog_postcontent_changelist",
            ),
        ]
        urls.extend(super().get_urls())
        return urls

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
        content_obj = self.get_content_obj_for_grouper(obj)
        if self.can_change(request, content_obj):
            return {"slug": ("title",)}
        return {}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj or form.instance, form, change)
        content_dict = {
            field: form.cleaned_data[field] for field in form._postcontent_fields if field in form.cleaned_data
        }
        if form.content_instance is None or form.content_instance.pk is None:
            PostContent.objects.with_user(request.user).create(
                post=form.instance,
                language=form.language,
                **content_dict,
            )
        else:
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

    class Media:
        js = ("admin/js/jquery.init.js", "djangocms_versioning/js/indicators.js", "djangocms_blog/js/language-selector.js")
        css = {"all": ("{}djangocms_blog/css/{}".format(settings.STATIC_URL, "djangocms_blog_admin.css"),
                       static_with_version("cms/css/cms.pagetree.css"),
                       "djangocms_versioning/css/actions.css",
                       )}


@admin.register(BlogConfig)
class BlogConfigAdmin(TranslatableAdmin):
    @property
    def declared_fieldsets(self):
        return self.get_fieldsets(None)

    def get_fieldsets(self, request, obj=None):
        """
        Fieldsets configuration
        """
        return [
            (None, {"fields": (
                "namespace",
                ("app_title", "object_name"),
            )}),
            (
                _("Generic"),
                {
                    "fields": (
                        ("use_placeholder",
                        "use_abstract",
                        "set_author"),
                        "use_related",
                    )
                },
            ),
            (
                _("Layout"),
                {
                    "fields": (
                        "paginate_by",
                        ("urlconf", "url_patterns"),
                        ("menu_structure", "menu_empty_categories"),
                        "template_prefix",
                        ("default_image_full", "default_image_thumbnail"),
                    ),
                    "classes": ("collapse",),
                },
            ),
            (
                _("Notifications"),
                {"fields": ("send_knock_create", "send_knock_update"), "classes": ("collapse",)},
            ),
            (
                _("Sitemap"),
                {
                    "fields": (
                        "sitemap_changefreq",
                        "sitemap_priority",
                    ),
                    "classes": ("collapse",),
                },
            ),
            (_("Meta"), {"fields": ("object_type",)}),
            (
                "Open Graph",
                {
                    "fields": (
                        "og_type",
                        ("og_app_id", "og_profile_id"),
                        "og_publisher",
                        ("og_author_url", "og_author"),
                    ),
                    "classes": ("collapse",),
                    "description": _("You can provide plain strings, Post model attribute or method names"),
                },
            ),
            (
                "Twitter",
                {
                    "fields": (
                        "twitter_type",
                        "twitter_site",
                        "twitter_author",
                    ),
                    "classes": ("collapse",),
                    "description": _("You can provide plain strings, Post model attribute or method names"),
                },
            ),
            (
                "Schema.org",
                {
                    "fields": (
                        "gplus_type",
                        "gplus_author",
                    ),
                    "classes": ("collapse",),
                    "description": _("You can provide plain strings, Post model attribute or method names"),
                },
            ),
        ]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk:
            return tuple(self.readonly_fields) + ("namespace",)
        else:
            return self.readonly_fields

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
