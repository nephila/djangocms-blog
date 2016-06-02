# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import include, url

urlpatterns = [
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
]
