from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import CustomUser, PostExtension


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Sites"), {"fields": ("sites",)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)


class PostExtensionInline(admin.TabularInline):
    model = PostExtension
    fields = ["some_field"]
    classes = ["collapse"]
    extra = 1
    can_delete = False
    verbose_name = "PostExtension"
    verbose_name_plural = "PostExtensions"
