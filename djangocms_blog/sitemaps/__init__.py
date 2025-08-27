from cms.utils import get_language_list
from django.contrib.sitemaps import Sitemap
from django.urls.exceptions import NoReverseMatch

from ..models import Post, PostContent
from ..settings import get_setting


class BlogSitemap(Sitemap):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_cache = {}

    def priority(self, obj: PostContent):
        if obj and obj.app_config:
            return obj.app_config.sitemap_priority
        return get_setting("SITEMAP_PRIORITY_DEFAULT")

    def changefreq(self, obj: PostContent):
        if obj and obj.app_config:
            return obj.app_config.sitemap_changefreq
        return get_setting("SITEMAP_CHANGEFREQ_DEFAULT")

    def location(self, obj: PostContent) -> str:
        return self.url_cache[obj]

    def items(self) -> list[PostContent]:
        items = []
        self.url_cache.clear()
        for lang in get_language_list():
            postcontents = PostContent.objects.filter(language=lang)
            for postcontent in postcontents:
                # check if the post actually has a url before appending
                # if a post is published but the associated app config is not
                # then this post will not have a url
                try:
                    self.url_cache[postcontent] = postcontent.get_absolute_url()
                except NoReverseMatch:
                    # couldn't determine the url of the post so pass on it
                    continue
                items.append(postcontent)
        return items

    def lastmod(self, obj: PostContent):
        return obj.post.date_modified
