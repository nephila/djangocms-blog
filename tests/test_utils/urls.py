# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.utils.conf import get_cms_setting
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'^media/cms/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': get_cms_setting('MEDIA_ROOT'), 'show_indexes': True}),
    url(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
)

urlpatterns += staticfiles_urlpatterns()

urlpatterns += i18n_patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^blog/', include('djangocms_blog.urls', namespace='djangocms_blog')),
    url(r'^', include('cms.urls')),
)
