from django.urls import path

from .feeds import FBInstantArticles, LatestEntriesFeed, TagFeed
from .settings import get_setting
from .views import (
    AuthorEntriesView,
    CategoryEntriesView,
    CategoryListView,
    PostArchiveView,
    PostDetailView,
    PostListView,
    TaggedListView,
)

app_name = "djangocms_blog"
urlpatterns = [
    path("", PostListView.as_view(), name="posts-latest"),
    path("category/", CategoryListView.as_view(), name="categories-all"),
    path("category/<str:category>/", CategoryEntriesView.as_view(), name="posts-category"),
    path("feed/", LatestEntriesFeed(), name="posts-latest-feed"),
    path("feed/fb/", FBInstantArticles(), name="posts-latest-feed-fb"),
    path("<int:year>/", PostArchiveView.as_view(), name="posts-archive"),
    path("<int:year>/<int:month>/", PostArchiveView.as_view(), name="posts-archive"),
    path("author/<str:username>/", AuthorEntriesView.as_view(), name="posts-author"),
    path("tag/<slug:tag>/", TaggedListView.as_view(), name="posts-tagged"),
    path("tag/<slug:tag>/feed/", TagFeed(), name="posts-tagged-feed"),
]
permalink_urls = get_setting("PERMALINK_URLS")
for urlconf in permalink_urls.values():
    urlpatterns.append(
        path(urlconf, PostDetailView.as_view(), name="post-detail"),
    )
