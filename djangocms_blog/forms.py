from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.utils.functional import cached_property
from parler.forms import TranslatableModelForm
from taggit_autosuggest.widgets import TagAutoSuggest

from .models import BlogCategory, BlogConfig, Post
from .settings import PERMALINK_TYPE_CATEGORY, get_setting

User = get_user_model()


class ConfigFormBase:
    """Base form class for all models depends on app_config."""

    @cached_property
    def app_config(self):
        """
        Return the currently selected app_config, whether it's an instance attribute or passed in the request
        """
        if getattr(self.instance, "app_config_id", None):
            return self.instance.app_config
        elif "app_config" in self.initial:
            return BlogConfig.objects.get(pk=self.initial["app_config"])
        elif self.data.get("app_config", None):
            return BlogConfig.objects.get(pk=self.data["app_config"])
        return None


class CategoryAdminForm(ConfigFormBase, TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        self.base_fields["meta_description"].validators = [MaxLengthValidator(get_setting("META_DESCRIPTION_LENGTH"))]
        original_attrs = self.base_fields["meta_description"].widget.attrs
        if "cols" in original_attrs:
            del original_attrs["cols"]
        if "rows" in original_attrs:
            del original_attrs["rows"]
        original_attrs["maxlength"] = get_setting("META_DESCRIPTION_LENGTH")
        self.base_fields["meta_description"].widget = forms.TextInput(original_attrs)
        super().__init__(*args, **kwargs)

        if "parent" in self.fields:
            qs = self.fields["parent"].queryset
            if self.instance.pk:
                qs = qs.exclude(pk__in=[self.instance.pk] + [child.pk for child in self.instance.descendants()])
            config = None
            if getattr(self.instance, "app_config_id", None):
                qs = qs.filter(app_config__namespace=self.instance.app_config.namespace)
            elif "app_config" in self.initial:
                config = BlogConfig.objects.get(pk=self.initial["app_config"])
            elif self.data.get("app_config", None):
                config = BlogConfig.objects.get(pk=self.data["app_config"])
            if config:
                qs = qs.filter(app_config__namespace=config.namespace)
            self.fields["parent"].queryset = qs

    class Meta:
        model = BlogCategory
        fields = "__all__"


class BlogPluginForm(forms.ModelForm):
    """Base plugin form to inject the list of configured template folders from BLOG_PLUGIN_TEMPLATE_FOLDERS."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "template_folder" in self.fields:
            self.fields["template_folder"].choices = get_setting("PLUGIN_TEMPLATE_FOLDERS")


class LatestEntriesForm(BlogPluginForm):
    """Custom forms for BlogLatestEntriesPlugin to properly load taggit-autosuggest."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].widget = TagAutoSuggest("taggit.Tag")

    class Media:
        css = {"all": ("djangocms_blog/css/djangocms_blog_admin.css",)}


class AuthorPostsForm(BlogPluginForm):
    """Custom form for BlogAuthorPostsPlugin to apply distinct to the list of authors in plugin changeform."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # apply distinct due to django issue #11707
        self.fields["authors"].queryset = User.objects.filter(djangocms_blog_post_author__publish=True).distinct()


# class PostAdminBaseForm(ConfigFormBase, forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         self.base_fields["meta_description"].validators = [MaxLengthValidator(get_setting("META_DESCRIPTION_LENGTH"))]
#         original_attrs = self.base_fields["meta_description"].widget.attrs
#         if "cols" in original_attrs:
#             del original_attrs["cols"]
#         if "rows" in original_attrs:
#             del original_attrs["rows"]
#         original_attrs["maxlength"] = get_setting("META_DESCRIPTION_LENGTH")
#         self.base_fields["meta_description"].widget = forms.TextInput(original_attrs)
#         self.base_fields["meta_title"].validators = [MaxLengthValidator(get_setting("META_TITLE_LENGTH"))]
#         super().__init__(*args, **kwargs)
#         if "categories" in self.fields:
#             if self.app_config and self.app_config.url_patterns == PERMALINK_TYPE_CATEGORY:
#                 self.fields["categories"].required = True
#             self.fields["categories"].queryset = self.available_categories
#         if "related" in self.fields:
#             self.fields["related"].queryset = self.available_related_posts
#
#         if "app_config" in self.fields:
#             # Don't allow app_configs to be added here. The correct way to add an
#             # apphook-config is to create an apphook on a cms Page.
#             self.fields["app_config"].widget.can_add_related = False
#
#         if self.app_config:
#             if not self.initial.get("main_image_full", ""):
#                 self.initial["main_image_full"] = self.app_config.app_data["config"].get("default_image_full")
#             if not self.initial.get("main_image_thumbnail", ""):
#                 self.initial["main_image_thumbnail"] = self.app_config.app_data["config"].get(
#                     "default_image_thumbnail"
#                 )


class PostAdminFormBase(ConfigFormBase, forms.ModelForm):
    """
    Common methods between the admin and wizard form
    """

    class Meta:
        model = Post
        fields = "__all__"

    @cached_property
    def available_categories(self):
        qs = BlogCategory.objects
        if self.app_config:
            return qs.filter(app_config__namespace=self.app_config.namespace)
        return qs

    @cached_property
    def available_related_posts(self):
        qs = Post.objects
        if self.app_config:
            if self.app_config.use_related == "1":
                qs = qs.filter(app_config__namespace=self.app_config.namespace)
        return qs


class PostAdminForm(PostAdminFormBase):
    def __init__(self, *args, **kwargs):
        if "meta_description" in self.base_fields:
            # Not available for published fields
            self.base_fields["meta_description"].validators = [
                MaxLengthValidator(get_setting("META_DESCRIPTION_LENGTH"))
            ]
            original_attrs = self.base_fields["meta_description"].widget.attrs
            if "cols" in original_attrs:
                del original_attrs["cols"]
            if "rows" in original_attrs:
                del original_attrs["rows"]
            original_attrs["maxlength"] = get_setting("META_DESCRIPTION_LENGTH")
            self.base_fields["meta_description"].widget = forms.TextInput(original_attrs)
        if "meta_title" in self.base_fields:
            self.base_fields["meta_title"].validators = [MaxLengthValidator(get_setting("META_TITLE_LENGTH"))]
        super().__init__(*args, **kwargs)
        if "categories" in self.fields:
            if getattr(self.app_config, "url_patterns", "") == PERMALINK_TYPE_CATEGORY:
                self.fields["categories"].required = True
            self.fields["categories"].queryset = self.available_categories
        if "related" in self.fields:
            self.fields["related"].queryset = self.available_related_posts

        if "app_config" in self.fields:
            # Don't allow app_configs to be added here. The correct way to add an
            # apphook-config is to create an apphook on a cms Page.
            self.fields["app_config"].widget.can_add_related = False

        if self.app_config:
            if not self.initial.get("main_image_full", ""):
                self.initial["main_image_full"] = self.app_config.default_image_full
            if not self.initial.get("main_image_thumbnail", ""):
                self.initial["main_image_thumbnail"] = self.app_config.default_image_thumbnail
