"""
This urlconf exists so we can run tests without an actual
Django project (Django expects ROOT_URLCONF to exist.)
It is not used by installed instances of this app.
"""

from django.urls import include, path

urlpatterns = [
    path("foo/", include("myapp.urls")),
]
