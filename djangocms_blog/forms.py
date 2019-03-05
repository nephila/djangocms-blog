# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django import forms
from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.utils.functional import cached_property
from parler.forms import TranslatableModelForm
from taggit_autosuggest.widgets import TagAutoSuggest

from .models import BlogCategory, BlogConfig, Post
from .settings import PERMALINK_TYPE_CATEGORY, get_setting


class ConfigFormBase(object):
    """
    This provide the app_config property which returns the currently
    selected app_config, whether it's an instance attribute or
    passed in the request
    """

    @cached_property
    def app_config(self):
        if getattr(self.instance, 'app_config_id', None):
            return self.instance.app_config
        elif 'app_config' in self.initial:
            return BlogConfig.objects.get(pk=self.initial['app_config'])
        elif self.data.get('app_config', None):
            return BlogConfig.objects.get(pk=self.data['app_config'])
        return None


class CategoryAdminForm(ConfigFormBase, TranslatableModelForm):

    def __init__(self, *args, **kwargs):
        self.base_fields['meta_description'].validators = [
            MaxLengthValidator(get_setting('META_DESCRIPTION_LENGTH'))
        ]
        original_attrs = self.base_fields['meta_description'].widget.attrs
        if 'cols' in original_attrs:
            del original_attrs['cols']
        if 'rows' in original_attrs:
            del original_attrs['rows']
        original_attrs['maxlength'] = get_setting('META_DESCRIPTION_LENGTH')
        self.base_fields['meta_description'].widget = forms.TextInput(original_attrs)
        super(CategoryAdminForm, self).__init__(*args, **kwargs)

        if 'parent' in self.fields:
            qs = self.fields['parent'].queryset
            if self.instance.pk:
                qs = qs.exclude(
                    pk__in=[self.instance.pk] + [child.pk for child in self.instance.descendants()]
                )
            config = None
            if getattr(self.instance, 'app_config_id', None):
                qs = qs.namespace(self.instance.app_config.namespace)
            elif 'app_config' in self.initial:
                config = BlogConfig.objects.get(pk=self.initial['app_config'])
            elif self.data.get('app_config', None):
                config = BlogConfig.objects.get(pk=self.data['app_config'])
            if config:
                qs = qs.namespace(config.namespace)
            self.fields['parent'].queryset = qs

    class Meta:
        model = BlogCategory
        fields = '__all__'


class LatestEntriesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LatestEntriesForm, self).__init__(*args, **kwargs)
        self.fields['tags'].widget = TagAutoSuggest('taggit.Tag')

    class Media:
        css = {
            'all': ('%sdjangocms_blog/css/%s' % (
                settings.STATIC_URL, 'djangocms_blog_admin.css'
            ),)
        }


class PostAdminFormBase(ConfigFormBase, TranslatableModelForm):
    """
    This provide common methods between the admin and wizard form
    """

    class Meta:
        model = Post
        fields = '__all__'

    @cached_property
    def available_categories(self):
        qs = BlogCategory.objects
        if self.app_config:
            return qs.namespace(self.app_config.namespace).active_translations()
        return qs

    def _post_clean_translation(self, translation):
        # This is a quickfix for https://github.com/django-parler/django-parler/issues/236
        # which needs to be fixed in parler
        # operating at form level ensure that if the model is validated outside the form
        # the uniqueness check is not disabled
        super(PostAdminFormBase, self)._post_clean_translation(translation)
        self._validate_unique = False


class PostAdminForm(PostAdminFormBase):

    def __init__(self, *args, **kwargs):
        self.base_fields['meta_description'].validators = [
            MaxLengthValidator(get_setting('META_DESCRIPTION_LENGTH'))
        ]
        original_attrs = self.base_fields['meta_description'].widget.attrs
        if 'cols' in original_attrs:
            del original_attrs['cols']
        if 'rows' in original_attrs:
            del original_attrs['rows']
        original_attrs['maxlength'] = get_setting('META_DESCRIPTION_LENGTH')
        self.base_fields['meta_description'].widget = forms.TextInput(original_attrs)
        self.base_fields['meta_title'].validators = [
            MaxLengthValidator(get_setting('META_TITLE_LENGTH'))
        ]
        super(PostAdminForm, self).__init__(*args, **kwargs)
        if 'categories' in self.fields:
            if self.app_config and self.app_config.url_patterns == PERMALINK_TYPE_CATEGORY:
                self.fields['categories'].required = True
            self.fields['categories'].queryset = self.available_categories

        if 'app_config' in self.fields:
            # Don't allow app_configs to be added here. The correct way to add an
            # apphook-config is to create an apphook on a cms Page.
            self.fields['app_config'].widget.can_add_related = False

        if self.app_config:
            if not self.initial.get('main_image_full', ''):
                self.initial['main_image_full'] = \
                    self.app_config.app_data['config'].get('default_image_full')
            if not self.initial.get('main_image_thumbnail', ''):
                self.initial['main_image_thumbnail'] = \
                    self.app_config.app_data['config'].get('default_image_thumbnail')
