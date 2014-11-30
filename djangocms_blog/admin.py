# -*- coding: utf-8 -*-
from admin_enhancer.admin import EnhancedModelAdminMixin
from cms.admin.placeholderadmin import PlaceholderAdminMixin, FrontendEditableAdminMixin
from copy import deepcopy
from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model
from parler.admin import TranslatableAdmin

from .forms import PostAdminForm
from .models import Post, BlogCategory
from .settings import get_setting


class BlogCategoryAdmin(EnhancedModelAdminMixin, TranslatableAdmin):
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

    class Media:
        css = {
            'all': ('%sdjangocms_blog/css/%s' % (settings.STATIC_URL,
                                                 'djangocms_blog_admin.css'),)
        }


class PostAdmin(EnhancedModelAdminMixin, FrontendEditableAdminMixin,
                PlaceholderAdminMixin, TranslatableAdmin, admin.ModelAdmin):
    form = PostAdminForm
    list_display = ['title', 'author', 'date_published', 'date_published_end']
    date_hierarchy = 'date_published'
    raw_id_fields = ['author']
    frontend_editable_fields = ('title', 'abstract', 'post_text')
    enhance_exclude = ('main_image', 'tags')
    _fieldsets = [
        (None, {
            'fields': [('title', 'slug', 'publish'), 'abstract']
        }),
        ('Info', {
            'fields': (['categories', 'tags'],
                       ('date_published', 'date_published_end', 'enable_comments')),
            'classes': ('collapse',)
        }),
        ('Immagine', {
            'fields': (('main_image', 'main_image_thumbnail', 'main_image_full'),),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': [('meta_description', 'meta_title', 'meta_keywords')],
            'classes': ('collapse',)
        }),
    ]

    def get_fieldsets(self, request, obj=None):
        fsets = deepcopy(self._fieldsets)
        if not get_setting('USE_PLACEHOLDER'):
            fsets[0][1]['fields'].append('post_text')
        if get_setting('MULTISITE'):
            fsets[1][1]['fields'][0].append('sites')
        if request.user.is_superuser:
            fsets[1][1]['fields'][0].append('author')
        return fsets

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        if not obj.author_id and get_setting('AUTHOR_DEFAULT'):
            if get_setting('AUTHOR_DEFAULT') is True:
                user = request.user
            else:
                user = get_user_model().objects.get(username=get_setting('AUTHOR_DEFAULT'))
            obj.author = user
        super(PostAdmin, self).save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('%sdjangocms_blog/css/%s' % (settings.STATIC_URL,
                                                 'djangocms_blog_admin.css'),)
        }


admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(Post, PostAdmin)
