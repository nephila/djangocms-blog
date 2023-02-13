from cms.models import PageContent
from cms.utils.i18n import get_language_dict, get_site_language_from_request
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import MaxLengthValidator
from django.urls import Resolver404, reverse
from django.utils.functional import cached_property
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from parler.forms import TranslatableModelForm
from taggit_autosuggest.widgets import TagAutoSuggest

from djangocms_blog import models

from .fields import LanguageSelector
from .models import BlogCategory, BlogConfig, Post, PostContent
from .settings import PERMALINK_TYPE_CATEGORY, get_setting

User = get_user_model()


def _get_options_from_model(model, fieldname):
    opt_keys = ("max_length", )
    for field in model._meta.fields:
        if field.name == fieldname:
            return {
                **{key: getattr(field, key) for key in opt_keys if hasattr(field, key)},
                **dict(
                    required=not field.blank,
                    label=field.verbose_name,
                    help_text=field.help_text,
                )
            }
    raise ImproperlyConfigured(f"Field '{fieldname} not found in model {model}")


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
                qs = qs.namespace(self.instance.app_config.namespace)
            elif "app_config" in self.initial:
                config = BlogConfig.objects.get(pk=self.initial["app_config"])
            elif self.data.get("app_config", None):
                config = BlogConfig.objects.get(pk=self.data["app_config"])
            if config:
                qs = qs.namespace(config.namespace)
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
        css = {"all": ("{}djangocms_blog/css/{}".format(settings.STATIC_URL, "djangocms_blog_admin.css"),)}


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
        labels = {
            # For and only for the fields from post content we need labels
            "slug": _("slug"),
            "title": _("title"),
            "subtitle": _("subtitle"),
            "meta_description": _("meta_description"),
            "meta_keywords": _("meta_keywords"),
            "meta_title": _("meta_title"),
        }

    @property
    def _postcontent_fields(self):
        return tuple(self._meta.labels.keys())

    title = forms.CharField(**_get_options_from_model(models.PostContent, "title"))
    subtitle = forms.CharField(**_get_options_from_model(models.PostContent, "subtitle"))
    slug = forms.CharField(
        validators = [validators.validate_unicode_slug],
        **_get_options_from_model(models.PostContent, "slug"),
    )

    meta_description = forms.CharField(
        **_get_options_from_model(models.PostContent, "meta_description"),
        widget=forms.Textarea,
    )
    meta_keywords = forms.CharField(**_get_options_from_model(models.PostContent, "meta_keywords"))
    meta_title = forms.CharField(**_get_options_from_model(models.PostContent, "meta_title"))
    language = forms.CharField(widget=forms.HiddenInput)

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
            if self.app_config.get("use_related", "0") == "1":
                qs = qs.filter(app_config__namespace=self.app_config.namespace)
        return qs

    def __init__(self, *args, **kwargs):
        """Identify language and fetch corresponding latest content object"""
        assert hasattr(self, "language") and self.language
        kwargs["initial"] = {
            "language": self.language,
            **kwargs.get("initial", {}),
        }
        self.content_instance = kwargs.get("content_instance", None)
        if "instance" in kwargs and kwargs["instance"]:
            # Instance provided? Get corresponding content object
            self.content_instance = kwargs["instance"].postcontent_set(manager="admin_manager") \
                .filter(language=self.language).latest_content().first()
        else:
            self.content_instance = None
        if self.content_instance is not None:
            kwargs["initial"] = {
                **{field: getattr(self.content_instance, field) for field in self._postcontent_fields},
                **kwargs.get("initial", {})
            }
        super().__init__(*args, **kwargs)
        language_dict = get_language_dict()
        for field in self._postcontent_fields:
            if field in self.fields:
                self.fields[field].label += f" ({language_dict[self.language]})"

    def clean(self):
        if self.cleaned_data.get("language", None) not in get_language_dict():
            raise ValidationError(
                _("Invalid language %(value)s. This form cannot be processed. Try changing languages."),
                params=dict(value=self.cleaned_data.get("language", _("<unspecified>"))),
                code="invalid-language",
            )


class PostAdminForm(PostAdminFormBase):
    def __init__(self, *args, **kwargs):
        if "meta_description" in self.base_fields:
            # Not available for published fields
            self.base_fields["meta_description"].validators = [MaxLengthValidator(get_setting("META_DESCRIPTION_LENGTH"))]
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
            if self.app_config and self.app_config.url_patterns == PERMALINK_TYPE_CATEGORY:
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
                self.initial["main_image_full"] = self.app_config.app_data["config"].get("default_image_full")
            if not self.initial.get("main_image_thumbnail", ""):
                self.initial["main_image_thumbnail"] = self.app_config.app_data["config"].get(
                    "default_image_thumbnail"
                )
