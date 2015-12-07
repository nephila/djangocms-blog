# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from taggit_autosuggest.widgets import TagAutoSuggest
from django.forms.fields import CharField

from djangocms_blog.models import BlogCategory


class LatestEntriesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LatestEntriesForm, self).__init__(*args, **kwargs)
        # self.fields['tags'].widget = TagAutoSuggest('taggit.Tag')
        for field_name in self.fields:
            if field_name == "categories":
                formfield = self.fields[field_name]
                if hasattr(formfield, 'queryset'):
                    formfield.queryset = BlogCategory.objects.filter(
                        sites=Site.objects.get_current())

    class Media:
        css = {
            'all': ('%sdjangocms_blog/css/%s' % (settings.STATIC_URL,
                                                 'djangocms_blog_admin.css'),)
        }


class UnuniqueSlugField(CharField):
    def clean(self, value):
        value = self.to_python(value).strip()
        return super(UnuniqueSlugField, self).clean(value)