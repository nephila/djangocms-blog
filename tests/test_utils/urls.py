# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import sys

from cms.sitemaps import CMSSitemap
from cms.utils.conf import get_cms_setting
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.i18n import javascript_catalog
from django.views.static import serve

from djangocms_blog.sitemaps import BlogSitemap

admin.autodiscover()

urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^media/cms/(?P<path>.*)$', serve,
        {'document_root': get_cms_setting('MEDIA_ROOT'), 'show_indexes': True}),
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog),
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {
            'cmspages': CMSSitemap, 'blog': BlogSitemap,
        }
        }),
]

urlpatterns += staticfiles_urlpatterns()

if 'server' not in sys.argv:
    urlpatterns += i18n_patterns(
        url(r'^blog/', include(
            'djangocms_blog.urls', namespace='djangocms_blog', app_name='djangocms_blog'
        )),
    )
urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('cms.urls')),
)
