# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django import forms
from django.conf import settings
from parler.forms import TranslatableModelForm
from taggit_autosuggest.widgets import TagAutoSuggest

from .models import BlogCategory, BlogConfig, Post


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
        super(PostAdminForm, self).__init__(*args, **kwargs)

        qs = BlogCategory.objects

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
