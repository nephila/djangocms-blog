# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from copy import deepcopy

from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from cms.admin.placeholderadmin import FrontendEditableAdminMixin, PlaceholderAdminMixin
from cms.models import CMSPlugin, ValidationError
from django import forms
from django.apps import apps
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.six import callable, text_type
from django.utils.translation import get_language_from_request, ugettext_lazy as _
from parler.admin import TranslatableAdmin

from .cms_appconfig import BlogConfig
from .forms import CategoryAdminForm, PostAdminForm
from .models import BlogCategory, Post
from .settings import get_setting

try:
    from admin_enhancer.admin import EnhancedModelAdminMixin
except ImportError:
    class EnhancedModelAdminMixin(object):
        pass


class SiteListFilter(admin.SimpleListFilter):
    title = _('site')
    parameter_name = 'sites'

    def lookups(self, request, model_admin):
        restricted_sites = model_admin.get_restricted_sites(request).values_list('id', flat=True)

        qs = Site.objects.all()
        if restricted_sites:
            qs = qs.filter(id__in=restricted_sites)

        return [(site.id, text_type(site.name)) for site in qs]

    def queryset(self, request, queryset):
        try:
            if 'sites' in self.used_parameters:
                return queryset.on_site(Site.objects.get(pk=self.used_parameters['sites']))
            return queryset
        except Site.DoesNotExist as e:  # pragma: no cover
            raise admin.options.IncorrectLookupParameters(e)
        except ValidationError as e:  # pragma: no cover
            raise admin.options.IncorrectLookupParameters(e)


class BlogCategoryAdmin(EnhancedModelAdminMixin, ModelAppHookConfig, TranslatableAdmin):
    form = CategoryAdminForm
    list_display = [
        'name', 'parent', 'app_config', 'all_languages_column',
    ]

    def get_prepopulated_fields(self, request, obj=None):
        app_config_default = self._app_config_select(request, obj)
        if app_config_default is None and request.method == 'GET':
            return {}
        return {'slug': ('name',)}

    class Media:
        css = {
            'all': ('%sdjangocms_blog/css/%s' % (settings.STATIC_URL, 'djangocms_blog_admin.css'),)
        }


class PostAdmin(PlaceholderAdminMixin, FrontendEditableAdminMixin,
                ModelAppHookConfig, TranslatableAdmin):
    form = PostAdminForm
    list_display = [
        'title', 'author', 'date_published', 'app_config', 'all_languages_column',
        'date_published_end'
    ]
    search_fields = ('translations__title',)
    date_hierarchy = 'date_published'
    raw_id_fields = ['author']
    frontend_editable_fields = ('title', 'abstract', 'post_text')
    enhance_exclude = ('main_image', 'tags')
    _fieldsets = [
        (None, {
            'fields': [['title', 'categories', 'publish', 'app_config']]
        }),
        (_('Info'), {
            'fields': [['slug', 'tags'],
                       ['date_published', 'date_published_end', 'date_featured'],
                       ['enable_comments']],
            'classes': ('collapse',)
        }),
        (_('Images'), {
            'fields': [['main_image', 'main_image_thumbnail', 'main_image_full']],
            'classes': ('collapse',)
        }),
        (_('SEO'), {
            'fields': [['meta_description', 'meta_title', 'meta_keywords']],
            'classes': ('collapse',)
        }),
    ]

    app_config_values = {
        'default_published': 'publish'
    }
    _sites = None

    def get_list_filter(self, request):
        filters = ['app_config', 'publish', 'date_published']
        if get_setting('MULTISITE'):
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

    def get_urls(self):
        """
        Customize the modeladmin urls
        """
        urls = [
            url(r'^publish/([0-9]+)/$', self.admin_site.admin_view(self.publish_post),
                name='djangocms_blog_publish_article'),
        ]
        urls.extend(super(PostAdmin, self).get_urls())
        return urls

    def post_add_plugin(self, request, obj1, obj2=None):
        if isinstance(obj1, CMSPlugin):
            plugin = obj1
        elif isinstance(obj2, CMSPlugin):
            plugin = obj2
        if plugin.plugin_type in get_setting('LIVEBLOG_PLUGINS'):
            plugin = plugin.move(plugin.get_siblings().first(), 'first-sibling')
        if isinstance(obj1, CMSPlugin):
            return super(PostAdmin, self).post_add_plugin(request, plugin)
        elif isinstance(obj2, CMSPlugin):
            return super(PostAdmin, self).post_add_plugin(request, obj1, plugin)

    def publish_post(self, request, pk):
        """
        Admin view to publish a single post

        :param request: request
        :param pk: primary key of the post to publish
        :return: Redirect to the post itself (if found) or fallback urls
        """
        language = get_language_from_request(request, check_path=True)
        try:
            post = Post.objects.get(pk=int(pk))
            post.publish = True
            post.save()
            return HttpResponseRedirect(post.get_absolute_url(language))
        except Exception:
            try:
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            except KeyError:
                return HttpResponseRedirect(reverse('djangocms_blog:posts-latest'))

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'meta_description':
            original_attrs = field.widget.attrs
            original_attrs['maxlength'] = 160
            field.widget = forms.TextInput(original_attrs)
        elif db_field.name == 'meta_title':
            field.max_length = 70
        return field

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
        form = super(PostAdmin, self)._set_config_defaults(request, form, obj)
        sites = self.get_restricted_sites(request)
        if 'sites' in form.base_fields and sites.exists():
            form.base_fields['sites'].queryset = self.get_restricted_sites(request).all()
        return form

    def get_fieldsets(self, request, obj=None):
        """
        Customize the fieldsets according to the app settings

        :param request: request
        :param obj: post
        :return: fieldsets configuration
        """
        app_config_default = self._app_config_select(request, obj)
        if app_config_default is None and request.method == 'GET':
            return super(PostAdmin, self).get_fieldsets(request, obj)
        if not obj:
            config = app_config_default
        else:
            config = obj.app_config

        fsets = deepcopy(self._fieldsets)
        if config:
            if config.use_abstract:
                fsets[0][1]['fields'].append('abstract')
            if not config.use_placeholder:
                fsets[0][1]['fields'].append('post_text')
        else:
            if get_setting('USE_ABSTRACT'):
                fsets[0][1]['fields'].append('abstract')
            if not get_setting('USE_PLACEHOLDER'):
                fsets[0][1]['fields'].append('post_text')
        if get_setting('MULTISITE') and not self.has_restricted_sites(request):
            fsets[1][1]['fields'][0].append('sites')
        if request.user.is_superuser:
            fsets[1][1]['fields'][0].append('author')
        if apps.is_installed('djangocms_blog.liveblog'):
            fsets[1][1]['fields'][2].append('enable_liveblog')
        filter_function = get_setting('ADMIN_POST_FIELDSET_FILTER')
        if callable(filter_function):
            fsets = filter_function(fsets, request, obj=obj)
        return fsets

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        obj._set_default_author(request.user)
        super(PostAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        sites = self.get_restricted_sites(request)
        if sites.exists():
            pks = list(sites.all().values_list('pk', flat=True))
            qs = qs.filter(sites__in=pks)
        return qs.distinct()

    def save_related(self, request, form, formsets, change):
        if self.get_restricted_sites(request).exists():
            if 'sites' in form.cleaned_data:
                form_sites = form.cleaned_data.get('sites', [])
                removed = set(
                    self.get_restricted_sites(request).all()
                ).difference(form_sites)
                diff_original = set(
                    form.instance.sites.all()
                ).difference(removed).union(form_sites)
                form.cleaned_data['sites'] = diff_original
            else:
                form.instance.sites.add(
                    *self.get_restricted_sites(request).all().values_list('pk', flat=True)
                )
        super(PostAdmin, self).save_related(request, form, formsets, change)

    class Media:
        css = {
            'all': ('%sdjangocms_blog/css/%s' % (settings.STATIC_URL, 'djangocms_blog_admin.css'),)
        }


class BlogConfigAdmin(BaseAppHookConfig, TranslatableAdmin):

    @property
    def declared_fieldsets(self):
        return self.get_fieldsets(None)

    def get_fieldsets(self, request, obj=None):
        """
        Fieldsets configuration
        """
        return [
            (None, {
                'fields': ('type', 'namespace', 'app_title', 'object_name')
            }),
            (_('Generic'), {
                'fields': (
                    'config.default_published', 'config.use_placeholder', 'config.use_abstract',
                    'config.set_author',
                )
            }),
            (_('Layout'), {
                'fields': (
                    'config.paginate_by', 'config.url_patterns', 'config.template_prefix',
                    'config.menu_structure', 'config.menu_empty_categories',
                ),
                'classes': ('collapse',)
            }),
            (_('Notifications'), {
                'fields': (
                    'config.send_knock_create', 'config.send_knock_update'
                ),
                'classes': ('collapse',)
            }),
            (_('Sitemap'), {
                'fields': (
                    'config.sitemap_changefreq', 'config.sitemap_priority',
                ),
                'classes': ('collapse',)
            }),
            (_('Meta'), {
                'fields': (
                    'config.object_type',
                )
            }),
            ('Open Graph', {
                'fields': (
                    'config.og_type', 'config.og_app_id', 'config.og_profile_id',
                    'config.og_publisher', 'config.og_author_url', 'config.og_author',
                ),
                'description': _(
                    'You can provide plain strings, Post model attribute or method names'
                )
            }),
            ('Twitter', {
                'fields': (
                    'config.twitter_type', 'config.twitter_site', 'config.twitter_author',
                ),
                'description': _(
                    'You can provide plain strings, Post model attribute or method names'
                )
            }),
            ('Google+', {
                'fields': (
                    'config.gplus_type', 'config.gplus_author',
                ),
                'description': _(
                    'You can provide plain strings, Post model attribute or method names'
                )
            }),
        ]

    def save_model(self, request, obj, form, change):
        """
        Clear menu cache when changing menu structure
        """
        if 'config.menu_structure' in form.changed_data:
            from menus.menu_pool import menu_pool
            menu_pool.clear(all=True)
        return super(BlogConfigAdmin, self).save_model(request, obj, form, change)


admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(BlogConfig, BlogConfigAdmin)
