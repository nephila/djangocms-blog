# -*- coding: utf-8 -*-
from django.utils.encoding import force_text

from aldryn_search.helpers import get_plugin_index_data
from aldryn_search.utils import get_index_base, strip_tags

from haystack import indexes

from .models import Post
from .settings import get_setting


class PostIndex(get_index_base()):
    haystack_use_for_indexing = get_setting('ENABLE_SEARCH')

    index_title = True

    author = indexes.CharField(indexed=True)
    #category_ids = indexes.MultiValueField(null=True)
    #category_titles = indexes.MultiValueField(null=True)

    def get_author(self, post):
        return post.get_author()

    def get_title(self, post):
        return post.safe_translation_getter('title')

    def get_description(self, post):
        return post.get_description()

    def prepare_pub_date(self, post):
        return post.date_published.strftime("%Y-%m-%d %H:%M:%S")

    def index_queryset(self, using=None):
        self._get_backend(using)
        language = self.get_current_language(using)
        filter_kwargs = self.get_index_kwargs(language)
        qs = self.get_index_queryset(language)
        if filter_kwargs:
            return qs.translated(language, **filter_kwargs)
        return qs

    def get_index_queryset(self, language):
        return self.get_model().objects.published().active_translations(
            language_code=language)

    def get_model(self):
        return Post

    def get_search_data(self, post, language, request):
        abstract = post.safe_translation_getter('abstract')
        text_bits = [strip_tags(abstract)]
        text_bits.append(post.get_description())
        text_bits.append(get_keywords)
        for category in post.categories.all():
            text_bits.append(
                force_text(category.safe_translation_getter('name')))
        for tag in post.tags.all():
            text_bits.append(force_text(tag.name))
        if post.content:
            plugins = post.content.cmsplugin_set.filter(language=language)
            for base_plugin in plugins:
                content = get_plugin_index_data(base_plugin, request)
                text_bits.append(content)
        return ' '.join(text_bits)
