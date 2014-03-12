# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import (PostListView, PostDetailView, TaggedListView,
                    AuthorEntriesView, PostArchiveView, CategoryEntriesView)
from .feeds import LatestEntriesFeed, TagFeed


urlpatterns = patterns(
    '',
    url(r'^$', PostListView.as_view(), name='posts-latest'),
    url(r'^feed/$', LatestEntriesFeed(), name='posts-latest-feed'),
    url(r'^(?P<year>\d{4})/$', PostArchiveView.as_view(), name='posts-archive'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', PostArchiveView.as_view(), name='posts-archive'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/$', PostDetailView.as_view(), name='post-detail'),
    url(r'^author/(?P<username>[\w\.@+-]+)/$', AuthorEntriesView.as_view(), name='posts-author'),
    url(r'^category/(?P<category>[\w\.@+-]+)/$', CategoryEntriesView.as_view(), name='posts-category'),
    url(r'^tag/(?P<tag>[-\w]+)/$', TaggedListView.as_view(), name='posts-tagged'),
    url(r'^tag/(?P<tag>[-\w]+)/feed/$', TagFeed(), name='posts-tagged-feed'),
)
