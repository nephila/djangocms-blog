# This file is used on divio cloud only during automatic setup
from django.urls import path  # pragma: no cover
from django.urls import include

urlpatterns = [  # pragma: no cover
    path("taggit_autosuggest/", include("taggit_autosuggest.urls")),
]
