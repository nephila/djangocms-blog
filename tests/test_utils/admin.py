from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from djangocms_blog.admin import PostAdmin

from .models import CustomUser, PostExtension


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Sites"), {"fields": ("sites",)}),
    )


class CustomPostAdmin(PostAdmin):
    _fieldsets = [
        (None, {"fields": ["title", "subtitle", "slug", "publish", "categories"]}),
        (
            _("Info"),
            {
                "fields": [
                    ["tags"],
                    ["date_published", "date_published_end", "date_featured"],
                    "app_config",
                    "enable_comments",
                ],
                "classes": ("collapse",),
            },
        ),
        (
            _("Images"),
            {"fields": [["main_image", "main_image_thumbnail", "main_image_full"]], "classes": ("collapse",)},
        ),
        (_("SEO"), {"fields": [["meta_description", "meta_title", "meta_keywords"]], "classes": ("collapse",)}),
    ]
    _fieldset_extra_fields_position = {
        "abstract": [0, 1],
        "post_text": [0, 1],
        "sites": [1, 1, 0],
        "author": [1, 1],
        "enable_liveblog": None,
        "related": None,
    }


class PostExtensionInline(admin.TabularInline):
    model = PostExtension
    fields = ["some_field"]
    classes = ["collapse"]
    extra = 1
    can_delete = False
    verbose_name = "PostExtension"
    verbose_name_plural = "PostExtensions"
