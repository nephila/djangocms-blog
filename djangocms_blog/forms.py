# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
import django_select2
from parler.forms import TranslatableModelForm

from .models import Post


class LatestEntriesForm(forms.ModelForm):

    class Meta:
        widgets = {
            'tags': django_select2.Select2MultipleWidget
        }

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
