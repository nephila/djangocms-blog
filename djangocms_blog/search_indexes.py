try:
    from aldryn_search.helpers import get_plugin_index_data
    from aldryn_search.utils import get_index_base, strip_tags
    from django.utils.encoding import force_str
    from haystack import indexes
    from parler.utils.context import switch_language

    from .models import Post
    from .settings import get_setting

    class PostIndex(get_index_base()):
        haystack_use_for_indexing = get_setting("ENABLE_SEARCH")

        index_title = True

        author = indexes.CharField(indexed=True, model_attr="get_author")
        keywords = indexes.CharField(null=True)
        tags = indexes.CharField(null=True, model_attr="get_tags")
        post_text = indexes.CharField(null=True)

        def get_title(self, post):
            return post.get_title()

        def get_description(self, post):
            return post.get_description()

        def prepare_pub_date(self, post):
            return post.date_published

        def index_queryset(self, using=None):
            self._get_backend(using)
            language = self.get_current_language(using)
            filter_kwargs = self.get_index_kwargs(language)
            qs = self.get_index_queryset(language)
            if filter_kwargs:
                return qs.translated(language, **filter_kwargs)
            return qs

        def get_index_queryset(self, language):
            return self.get_model().objects.published().active_translations(language_code=language)

        def get_model(self):
            return Post

        def get_search_data(self, post, language, request):
            with switch_language(post, language):
                description = post.get_description()
                abstract = strip_tags(post.safe_translation_getter("abstract", default=""))
                keywords = post.get_keywords()

                text_bits = []
                if abstract:
                    text_bits.append(abstract)
                if description:
                    text_bits.append(description)
                if keywords:
                    text_bits.append(" ".join(keywords))
                    self.prepared_data["keywords"] = ",".join(keywords)
                for category in post.categories.all():
                    text_bits.append(force_str(category.safe_translation_getter("name")))
                for tag in post.tags.all():
                    text_bits.append(force_str(tag.name))

                if get_setting("USE_PLACEHOLDER"):
                    plugins = post.content.cmsplugin_set.filter(language=language)
                    content_bits = []
                    for base_plugin in plugins:
                        content = get_plugin_index_data(base_plugin, request)
                        content_bits.append(" ".join(content))
                    post_text = " ".join(content_bits)
                else:
                    post_text = post.safe_translation_getter("post_text")
                    if post_text:
                        post_text = strip_tags(post_text)
                self.prepared_data["post_text"] = post_text
                text_bits.append(post_text)

                return " ".join(text_bits)


except ImportError:
    pass
