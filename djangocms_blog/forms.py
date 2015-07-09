# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from parler.forms import TranslatableModelForm
from taggit_autosuggest.widgets import TagAutoSuggest

from .models import Post


class LatestEntriesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LatestEntriesForm, self).__init__(*args, **kwargs)
        # self.fields['tags'].widget = TagAutoSuggest('taggit.Tag')

    class Media:
        css = {
            'all': ('%sdjangocms_blog/css/%s' % (settings.STATIC_URL,
                                                 'djangocms_blog_admin.css'),)
        }


class PostAdminForm(TranslatableModelForm):

    def __init__(self, *args, **kwargs):
        super(PostAdminForm, self).__init__(*args, **kwargs)
        original_attrs = self.fields['meta_description'].widget.attrs
        original_attrs['maxlength'] = 160
        self.fields['meta_description'].widget = forms.TextInput(original_attrs)
        self.fields['meta_title'].max_length = 70

    class Meta:
        model = Post
        exclude = ()
