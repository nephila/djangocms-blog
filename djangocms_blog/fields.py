# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import django
from django.db.models import SlugField
from django.utils.text import slugify as django_slugify

__all__ = ['AutoSlugField']


class AutoSlugField(SlugField):
    def __init__(self, *args, **kwargs):
        if django.VERSION < (1, 9):
            self.allow_unicode = kwargs.pop('allow_unicode', False)
        super(AutoSlugField, self).__init__(*args, **kwargs)


def slugify(base):
    if django.VERSION >= (1, 9):
        return django_slugify(base, allow_unicode=True)
    else:
        return django_slugify(base)
