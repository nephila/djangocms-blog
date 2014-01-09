# -*- coding: utf-8 -*-
from admin_enhancer.admin import EnhancedModelAdminMixin
from cms.admin.placeholderadmin import PlaceholderAdmin, FrontendEditableAdmin
from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Post, BlogCategory


class BlogCategoryAdmin(EnhancedModelAdminMixin, TranslatableAdmin):
    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


class PostAdmin(EnhancedModelAdminMixin, FrontendEditableAdmin,
                PlaceholderAdmin, TranslatableAdmin):
    list_display = ['title', 'author', 'date_published', 'date_published_end']
    date_hierarchy = 'date_published'
    raw_id_fields = ['author']
    frontend_editable_fields = ("title", "abstract")
    enhance_exclude = ('main_image', 'tags')
    change_form_template = "admin/djangocms_blog/post_change_form.html"

    fieldsets = [
        (None, {
            'fields': [('title', 'slug', 'publish'),
                       ('categories', 'tags'),
                       ('date_published', 'date_published_end'), 'author']
        }),
        (None, {
            'fields': [('main_image', 'main_image_thumbnail', 'main_image_full'),
                       'abstract']
        }),
    ]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super(PostAdmin, self).save_model(request, obj, form, change)

admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(Post, PostAdmin)
