# -*- coding: utf-8 -*-
from aldryn_search.helpers import get_plugin_index_data
from aldryn_search.utils import get_index_base, strip_tags
from django.utils.encoding import force_text
from haystack import indexes

from .models import Post
from .settings import get_setting


class PostIndex(get_index_base()):
    haystack_use_for_indexing = get_setting('ENABLE_SEARCH')

    index_title = True

    author = indexes.CharField(indexed=True, model_attr='get_author')
    keywords = indexes.CharField(null=True)
    tags = indexes.CharField(null=True)
    post_text = indexes.CharField(null=True)

    def get_keywords(self, post):
        return ','.join(post.get_keywords())

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
        optional_attributes = []
        abstract = post.safe_translation_getter('abstract')
        text_bits = [post.get_title()]
        text_bits.append(strip_tags(abstract))
        text_bits.append(post.get_description())
        text_bits.append(' '.join(post.get_keywords()))
        for category in post.categories.all():
            text_bits.append(
                force_text(category.safe_translation_getter('name')))
        for tag in post.tags.all():
            text_bits.append(force_text(tag.name))
        if post.content:
            plugins = post.content.cmsplugin_set.filter(language=language)
            for base_plugin in plugins:
                content = get_plugin_index_data(base_plugin, request)
                text_bits.append(' '.join(content))
        for attribute in optional_attributes:
            value = force_text(getattr(post, attribute))
            if value and value not in text_bits:
                text_bits.append(value)
        return ' '.join(text_bits)

    def prepare_fields(self, post, language, request):
        super(PostIndex, self).prepare_fields(post, language, request)
        data = [self.prepared_data['text']]
        self.prepared_data['keywords'] = ' '.join(post.get_keywords())
        self.prepared_data['tags'] = ' '.join(post.get_tags())
        self.prepared_data['post_text'] = ' '.join(post.safe_translation_getter('post_text'))
        self.prepared_data['text'] = ' '.join(data)
