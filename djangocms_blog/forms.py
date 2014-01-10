# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
import django_select2


class LatestEntriesForm(forms.ModelForm):

    class Meta:
        widgets = {
            'tags': django_select2.Select2MultipleWidget
        }

    class Media:
        css = {
            'all': ('%sdjangocms_blog/css/%s' % (settings.STATIC_URL,
                                                  "djangocms_blog_admin.css"),)
        }