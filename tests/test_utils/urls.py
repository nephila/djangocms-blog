import sys

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve

from djangocms_blog.sitemaps import BlogSitemap

admin.autodiscover()

urlpatterns = [
    path("media/<str:path>", serve, {"document_root": settings.MEDIA_ROOT, "show_indexes": True}),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("taggit_autosuggest/", include("taggit_autosuggest.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": {"cmspages": CMSSitemap, "blog": BlogSitemap}}),
]

urlpatterns += staticfiles_urlpatterns()

if "server" not in sys.argv:
    urlpatterns += i18n_patterns(
        path("blog/", include("djangocms_blog.urls")),
    )
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("cms.urls")),
)
