# -*- coding: utf-8 -*-
from django.conf.urls import url

from djangocms_blog.feeds import FBInstantArticles, LatestEntriesFeed, TagFeed
from djangocms_blog.settings import get_setting
from djangocms_blog.views import (
    AuthorEntriesView, CategoryEntriesView, PostArchiveView, PostDetailView, PostListView,
    TaggedListView,
)


def get_urls():
    urls = get_setting('PERMALINK_URLS')
    details = []
    for urlconf in urls.values():
        details.append(
            url(urlconf, PostDetailView.as_view(), name='post-detail'),
        )
    return details


detail_urls = get_urls()

urlpatterns = [
    url(r'^latests/$',
        PostListView.as_view(), name='posts-latest'),
    url(r'^feed/$',
        LatestEntriesFeed(), name='posts-latest-feed'),
    url(r'^feed/fb/$',
        FBInstantArticles(), name='posts-latest-feed-fb'),
    url(r'^(?P<year>\d{4})/$',
        PostArchiveView.as_view(), name='posts-archive'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        PostArchiveView.as_view(), name='posts-archive'),
    url(r'^author/(?P<username>[\w\.@+-]+)/$',
        AuthorEntriesView.as_view(), name='posts-author'),
    url(r'^category/(?P<category>[\w\.@+-]+)/$',
        CategoryEntriesView.as_view(), name='posts-category'),
    url(r'^tag/(?P<tag>[-\w]+)/$',
        TaggedListView.as_view(), name='posts-tagged'),
    url(r'^tag/(?P<tag>[-\w]+)/feed/$',
        TagFeed(), name='posts-tagged-feed'),
] + detail_urls
