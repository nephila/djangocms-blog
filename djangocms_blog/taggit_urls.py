# This file is used on divio cloud only during automatic setup
from django.conf.urls import include  # pragma: no cover
from django.urls import path  # pragma: no cover

urlpatterns = [  # pragma: no cover
    path("taggit_autosuggest/", include("taggit_autosuggest.urls")),
]
