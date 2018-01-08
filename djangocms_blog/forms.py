# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django import forms
from django.conf import settings
from django.core.validators import MaxLengthValidator
from parler.forms import TranslatableModelForm
from taggit_autosuggest.widgets import TagAutoSuggest

from djangocms_blog.settings import get_setting

from .models import BlogCategory, BlogConfig, Post


class CategoryAdminForm(TranslatableModelForm):

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

            if getattr(self.instance, 'app_config_id', None):
                qs = qs.namespace(self.instance.app_config.namespace)
            elif 'initial' in kwargs and 'app_config' in kwargs['initial']:
                config = BlogConfig.objects.get(pk=kwargs['initial']['app_config'])
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
            'all': ('%sdjangocms_blog/css/%s' % (settings.STATIC_URL,
                                                 'djangocms_blog_admin.css'),)
        }


class PostAdminForm(TranslatableModelForm):

    class Meta:
        model = Post
        fields = '__all__'

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

        qs = BlogCategory.objects

        config = None
        if getattr(self.instance, 'app_config_id', None):
            qs = qs.namespace(self.instance.app_config.namespace)
        elif 'initial' in kwargs and 'app_config' in kwargs['initial']:
            config = BlogConfig.objects.get(pk=kwargs['initial']['app_config'])
            qs = qs.namespace(config.namespace)

        if 'categories' in self.fields:
            self.fields['categories'].queryset = qs

        if 'app_config' in self.fields:
            # Don't allow app_configs to be added here. The correct way to add an
            # apphook-config is to create an apphook on a cms Page.
            self.fields['app_config'].widget.can_add_related = False

        if config:
            self.initial['main_image_full'] = \
                config.app_data['config'].get('default_image_full')
            self.initial['main_image_thumbnail'] = \
                config.app_data['config'].get('default_image_thumbnail')
