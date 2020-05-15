# -*- coding: utf-8 -*-
from django.conf.urls import include, url

urlpatterns = [
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
]
