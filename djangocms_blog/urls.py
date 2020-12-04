from django.urls import path

from .feeds import FBInstantArticles, LatestEntriesFeed, TagFeed
from .settings import get_setting
from .views import (
    AuthorEntriesView,
    CategoryEntriesView,
    PostArchiveView,
    PostDetailView,
    PostListView,
    TaggedListView,
)


def get_urls():
    urls = get_setting("PERMALINK_URLS")
    details = []
    for urlconf in urls.values():
        details.append(
            path(urlconf, PostDetailView.as_view(), name="post-detail"),
        )
    return details


detail_urls = get_urls()

# module-level app_name attribute as per django 1.9+
app_name = "djangocms_blog"
urlpatterns = [
    path("", PostListView.as_view(), name="posts-latest"),
    path("feed/", LatestEntriesFeed(), name="posts-latest-feed"),
    path("feed/fb/", FBInstantArticles(), name="posts-latest-feed-fb"),
    path("<int:year>/", PostArchiveView.as_view(), name="posts-archive"),
    path("<int:year>/<int:month>/", PostArchiveView.as_view(), name="posts-archive"),
    path("author/<str:username>/", AuthorEntriesView.as_view(), name="posts-author"),
    path("category/<str:category>/", CategoryEntriesView.as_view(), name="posts-category"),
    path("tag/<slug:tag>/", TaggedListView.as_view(), name="posts-tagged"),
    path("tag/<slug:tag>/feed/", TagFeed(), name="posts-tagged-feed"),
] + detail_urls
