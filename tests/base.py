import json
import os
from copy import deepcopy

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from menus.menu_pool import menu_pool
from parler.utils.context import smart_override

from djangocms_blog.cms_appconfig import BlogConfig
from djangocms_blog.cms_menus import BlogCategoryMenu, BlogNavModifier
from djangocms_blog.models import BlogCategory, Post, PostContent, ThumbnailOption
from tests.base_test import BaseTestCase

User = get_user_model()


def _get_cat_pk(lang, name):
    return lambda: BlogCategory.objects.language(lang).translated(lang, name=name).get().pk


class BaseTest(BaseTestCase):
    """
    Base class with utility function
    """

    category_1 = None
    thumb_1 = None
    thumb_2 = None

    _pages_data = (
        {
            "en": {"title": "page one", "template": "blog.html", "publish": False},
            "fr": {"title": "page un", "publish": False},
            "it": {"title": "pagina uno", "publish": False},
        },
        {
            "en": {
                "title": "page two",
                "template": "blog.html",
                "publish": False,
                "apphook": "BlogApp",
                "apphook_namespace": "sample_app",
            },
            "fr": {"title": "page deux", "publish": False},
            "it": {"title": "pagina due", "publish": False},
        },
        {
            "en": {
                "title": "page three",
                "template": "blog.html",
                "publish": False,
                "apphook": "BlogApp",
                "apphook_namespace": "sample_app2",
            },
            "fr": {"title": "page trois", "publish": False},
            "it": {"title": "pagina tre", "publish": False},
        },
    )

    _post_data = (
        {
            "en": {
                "title": "First post",
                "abstract": "<p>first line</p>",
                "description": "This is the description",
                "keywords": "keyword1, keyword2",
                "text": "Post text",
                "app_config": "sample_app",
                "publish": True,
            },
            "it": {
                "title": "Primo post",
                "abstract": "<p>prima riga</p>",
                "description": "Questa è la descrizione",
                "keywords": "keyword1, keyword2",
                "text": "Testo del post",
            },
        },
        {
            "en": {
                "title": "Second post",
                "abstract": "<p>second post first line</p>",
                "description": "Second post description",
                "keywords": "keyword3, keyword4",
                "text": "Second post text",
                "app_config": "sample_app",
                "publish": False,
            },
            "it": {
                "title": "Secondo post",
                "abstract": "<p>prima riga del secondo post</p>",
                "description": "Descrizione del secondo post",
                "keywords": "keyword3, keyword4",
                "text": "Testo del secondo post",
                "app_config": "sample_app",
            },
        },
        {
            "en": {
                "title": "Third post",
                "abstract": "<p>third post first line</p>",
                "description": "third post description",
                "keywords": "keyword5, keyword6",
                "text": "Third post text",
                "app_config": "sample_app",
                "publish": False,
            },
            "it": {
                "title": "Terzo post",
                "abstract": "<p>prima riga del terzo post</p>",
                "description": "Descrizione del terzo post",
                "keywords": "keyword5, keyword6",
                "text": "Testo del terzo post",
            },
        },
        {
            "en": {
                "title": "Different appconfig",
                "abstract": "<p>Different appconfig first line</p>",
                "description": "Different appconfig description",
                "keywords": "keyword5, keyword6",
                "text": "Different appconfig text",
                "app_config": "sample_app2",
                "publish": True,
            },
            "it": {
                "title": "Altro appconfig",
                "abstract": "<p>prima riga del Altro appconfig</p>",
                "description": "Descrizione Altro appconfig",
                "keywords": "keyword5, keyword6",
                "text": "Testo del Altro appconfig",
            },
        },
    )

    _categories_data = (
        {"en": {"name": "Very loud", "app_config": "sample_app"}, "it": {"name": "Fortissimo"}},
        {"en": {"name": "Very very silent", "app_config": "sample_app"}, "it": {"name": "Pianississimo"}},
        {"en": {"name": "Almost", "app_config": "sample_app"}, "it": {"name": "Mezzo"}},
        {"en": {"name": "Drums", "app_config": "sample_app2"}, "it": {"name": "Tamburi"}},
        {"en": {"name": "Guitars", "app_config": "sample_app2"}, "it": {"name": "Chitarre"}},
        {
            "en": {"name": "Loud", "parent_id": _get_cat_pk("en", "Almost"), "app_config": "sample_app"},
            "it": {"name": "Forte", "parent_id": _get_cat_pk("it", "Mezzo")},
        },
        {"en": {"name": "Silent", "parent_id": _get_cat_pk("en", "Almost"), "app_config": "sample_app"}},
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thumb_1, __ = ThumbnailOption.objects.get_or_create(
            name="base", width=100, height=100, crop=True, upscale=False
        )
        cls.thumb_2, __ = ThumbnailOption.objects.get_or_create(
            name="main", width=200, height=200, crop=False, upscale=False
        )
        cls.app_config_1, __ = BlogConfig.objects.get_or_create(namespace="sample_app")
        cls.app_config_2, __ = BlogConfig.objects.get_or_create(namespace="sample_app2")
        cls.app_config_1.app_title = "app1"
        cls.app_config_1.object_name = "Blog"
        cls.app_config_1.paginate_by = 1
        cls.app_config_1.send_knock_create = True
        cls.app_config_1.send_knock_update = True
        cls.app_config_1.save()
        cls.app_config_2.app_title = "app2"
        cls.app_config_2.object_name = "Article"
        cls.app_config_2.paginate_by = 2
        cls.app_config_2.send_knock_create = True
        cls.app_config_2.send_knock_update = True
        cls.app_config_2.save()
        cls.app_configs = {
            "sample_app": cls.app_config_1,
            "sample_app2": cls.app_config_2,
        }
        cls.category_1 = BlogCategory.objects.create(name="category 1", app_config=cls.app_config_1)
        cls.category_1.set_current_language("it", initialize=True)
        cls.category_1.name = "categoria 1"
        cls.category_1.save()
        cls.site_2, __ = Site.objects.get_or_create(domain="http://example2.com", name="example 2")
        cls.site_3, __ = Site.objects.get_or_create(domain="http://example3.com", name="example 3")
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        cache.clear()
        super().tearDownClass()

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def get_nodes(self, menu_pool, request):
        try:
            nodes = menu_pool.get_renderer(request).get_nodes()
        except AttributeError:
            nodes = menu_pool.get_nodes(request)
        return nodes

    def _get_category(self, data, category=None, lang="en"):
        data = deepcopy(data)
        for k, v in data.items():
            if callable(v):
                data[k] = v()
        if not category:
            with smart_override(lang):
                data["app_config"] = self.app_configs[data["app_config"]]
                category = BlogCategory.objects.create(**data)
        else:
            category.set_current_language(lang, initialize=True)
            for attr, val in data.items():
                setattr(category, attr, val)
            category.save()
        return category

    def _get_post(self, data, post=None, lang="en", sites=None):
        if not post:
            post_data = {
                "author": self.user,
                "app_config": self.app_configs[data["app_config"]],
            }
            post = Post.objects.create(**post_data)
            post.postcontent_set.update_or_create(
                title=data["title"],
                abstract=data["abstract"],
                meta_description=data["description"],
                meta_keywords=data["keywords"],
                language=lang,
            )
        else:
            post.postcontent_set.update_or_create(
                title=data["title"],
                abstract=data["abstract"],
                meta_description=data["description"],
                meta_keywords=data["keywords"],
                language=lang,
            )
        post.categories.add(self.category_1)
        if sites:
            for site in sites:
                post.sites.add(site)
        return post

    def get_posts(self, sites=None):
        posts = []
        cache.clear()
        if Post.objects.all().exists():
            return list(Post.objects.all())
        for post in self._post_data:
            post1 = self._get_post(post["en"], sites=sites)
            post1 = self._get_post(post["it"], post=post1, lang="it")
            post1.publish = post["en"]["publish"]
            post1.main_image = self.create_filer_image_object()
            post1.save()
            posts.append(post1)
        return posts

    def get_post_index(self):
        from haystack import connections
        from haystack.constants import DEFAULT_ALIAS

        search_conn = connections[DEFAULT_ALIAS]
        unified_index = search_conn.get_unified_index()
        index = unified_index.get_index(Post)
        return index

    def _reset_menus(self):
        cache.clear()
        BlogCategoryMenu._config = {}
        BlogNavModifier._config = {}

    def _reload_menus(self):
        menu_pool.clear(all=True)
        menu_pool.discover_menus()
        # All cms menu modifiers should be removed from menu_pool.modifiers
        # so that they do not interfere with our menu nodes
        menu_pool.modifiers = [m for m in menu_pool.modifiers if m.__module__.startswith("djangocms_blog")]
        self._reset_menus()

    def read_json(self, path, raw=False):
        """
        Read a json file from the given path

        :param path: JSON file path (relative to the current test file
        :type path: str
        :param raw: return the file content without loading as a json object
        :type raw: bool
        :return json data (either raw or loaded)
        :type: (dict|str)
        """
        full_path = os.path.join(os.path.dirname(__file__), path)
        with open(full_path) as src:
            if raw:
                return src.read()
            else:
                return json.load(src)
