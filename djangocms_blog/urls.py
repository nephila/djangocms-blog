# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url

from .feeds import CategoryFeed, FBInstantArticles, LatestEntriesFeed, TagFeed
from .settings import get_setting
from .views import (
    AuthorEntriesView, CategoryEntriesView, PostArchiveView, PostDetailView, PostListView,
    TaggedListView,
)


def get_urls():
    urls = get_setting("PERMALINK_URLS")
    details = []
    for urlconf in urls.values():
        details.append(url(urlconf, PostDetailView.as_view(), name="post-detail"))
    return details


detail_urls = get_urls()

# module-level app_name attribute as per django 1.9+
app_name = "djangocms_blog"
urlpatterns = [
    url(r"^$", PostListView.as_view(), name="posts-latest"),
    url(r"^feed/$", LatestEntriesFeed(), name="posts-latest-feed"),
    url(r"^feed/fb/$", FBInstantArticles(), name="posts-latest-feed-fb"),
    url(r"^(?P<year>\d{4})/$", PostArchiveView.as_view(), name="posts-archive"),
    url(
        r"^(?P<year>\d{4})/(?P<month>\d{1,2})/$",
        PostArchiveView.as_view(),
        name="posts-archive",
    ),
    url(
        r"^author/(?P<username>[\w\.@+-]+)/$",
        AuthorEntriesView.as_view(),
        name="posts-author",
    ),
    url(
        r"^category/(?P<category>[\w\.@+-]+)/$",
        CategoryEntriesView.as_view(),
        name="posts-category",
    ),
    url(
        r"^category/(?P<category>[\w\.@+-]+)/feed/$",
        CategoryFeed(),
        name="posts-category-feed",
    ),
    url(
        r"^category/(?P<category>[\w\.@+-]+)/feed/(?P<feed_items_number>\d{1,4})/$",
        CategoryFeed(),
        name="posts-category-feed-items-number",
    ),
    url(r"^tag/(?P<tag>[-\w]+)/$", TaggedListView.as_view(), name="posts-tagged"),
    url(r"^tag/(?P<tag>[-\w]+)/feed/$", TagFeed(), name="posts-tagged-feed"),
    url(
        r"^tag/(?P<tag>[-\w]+)/feed/(?P<feed_items_number>\d{1,4})/$",
        TagFeed(),
        name="posts-tagged-feed-items-number",
    ),
] + detail_urls
