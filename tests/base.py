import json
import os
from collections import OrderedDict
from copy import deepcopy

from app_helper.base_test import BaseTestCase
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from menus.menu_pool import menu_pool
from parler.utils.context import smart_override

from djangocms_blog.cms_appconfig import BlogConfig
from djangocms_blog.cms_menus import BlogCategoryMenu, BlogNavModifier
from djangocms_blog.compat import CMS_4_PLUS
from djangocms_blog.models import BlogCategory, Post, ThumbnailOption

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
            "en": {"title": "page one", "template": "blog.html", "publish": True},
            "fr": {"title": "page un", "publish": True},
            "it": {"title": "pagina uno", "publish": True},
        },
        {
            "en": {
                "title": "page two",
                "template": "blog.html",
                "publish": True,
                "apphook": "BlogApp",
                "apphook_namespace": "sample_app",
            },
            "fr": {"title": "page deux", "publish": True},
            "it": {"title": "pagina due", "publish": True},
        },
        {
            "en": {
                "title": "page three",
                "template": "blog.html",
                "publish": True,
                "apphook": "BlogApp",
                "apphook_namespace": "sample_app2",
            },
            "fr": {"title": "page trois", "publish": True},
            "it": {"title": "pagina tre", "publish": True},
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
        cls.app_config_1.app_data.config.paginate_by = 1
        cls.app_config_1.app_data.config.send_knock_create = True
        cls.app_config_1.app_data.config.send_knock_update = True
        cls.app_config_1.save()
        cls.app_config_2.app_title = "app2"
        cls.app_config_2.object_name = "Article"
        cls.app_config_2.app_data.config.paginate_by = 2
        cls.app_config_2.app_data.config.send_knock_create = True
        cls.app_config_2.app_data.config.send_knock_update = True
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
                "title": data["title"],
                "abstract": data["abstract"],
                "meta_description": data["description"],
                "meta_keywords": data["keywords"],
                "app_config": self.app_configs[data["app_config"]],
            }
            post = Post.objects.create(**post_data)
        else:
            post.create_translation(
                lang,
                title=data["title"],
                abstract=data["abstract"],
                meta_description=data["description"],
                meta_keywords=data["keywords"],
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

    def _get_placeholder(self, page, slot, language="en"):
        """Get a placeholder from a page by slot name, compatible with CMS 3.x and 4.x."""
        try:
            # django CMS 3.x compatibility: Page.placeholders M2M field removed in CMS 4.x
            return page.placeholders.get(slot=slot)
        except AttributeError:  # CMS 4.x: Page.placeholders M2M field removed
            return page.get_placeholders(language).get(slot=slot)

    # django CMS 3.x compatibility: the overrides below replace app_helper's
    # CMS-3.x-only implementations of _prepare_request, get_toolbar_request,
    # and create_pages.  When CMS 3.x support is dropped, these can be removed
    # and app_helper updated to a version that supports CMS 4.x natively.
    if CMS_4_PLUS:
        def _prepare_request(self, request, page, user, lang, use_middlewares, use_toolbar=False, secure=False):
            """CMS 4.x: ToolbarMiddleware extends MiddlewareMixin, always needs get_response."""
            from http.cookies import SimpleCookie
            from importlib import import_module
            from io import StringIO

            from django.conf import settings as _settings
            from django.contrib.auth.models import AnonymousUser
            from django.http import HttpResponse
            from django.utils.functional import SimpleLazyObject

            engine = import_module(_settings.SESSION_ENGINE)
            request.current_page = SimpleLazyObject(lambda: page)
            if not user:
                if self._login_context:
                    user = self._login_context.user
                else:
                    user = AnonymousUser()
            if user.is_authenticated:
                session_key = user._meta.pk.value_to_string(user)
            else:
                session_key = "session_key"
            request.user = user
            request._cached_user = user
            request.session = engine.SessionStore(session_key)
            if secure:
                request.environ["SERVER_PORT"] = "443"
                request.environ["wsgi.url_scheme"] = "https"
            request.cookies = SimpleCookie()
            request.errors = StringIO()
            request.LANGUAGE_CODE = lang
            if request.method == "POST":
                request._dont_enforce_csrf_checks = True
            if use_middlewares:
                self._apply_middlewares(request)
            elif use_toolbar:
                from cms.middleware.toolbar import ToolbarMiddleware
                mid = ToolbarMiddleware(lambda req: HttpResponse())
                mid.process_request(request)
            return request

        def get_toolbar_request(self, page, user, path=None, edit=False, lang="en", use_middlewares=False, secure=False):
            """CMS 4.x override: CMS_TOOLBAR_URL__EDIT_ON renamed to CMS_TOOLBAR_URL__ENABLE.
            Also forces edit_mode_active=True since CMS 4.x no longer activates it via URL param."""
            from cms.utils.conf import get_cms_setting

            edit_on = get_cms_setting("CMS_TOOLBAR_URL__ENABLE")
            path = path or page and page.get_absolute_url(lang)
            if edit:
                path = "{}?{}".format(path, edit_on)
            from django.test import RequestFactory

            request = RequestFactory().get(path, secure=secure)
            request = self._prepare_request(request, page, user, lang, use_middlewares, use_toolbar=True, secure=secure)
            if edit and hasattr(request, "toolbar"):
                # CMS 4.x: edit_mode_active no longer triggered by URL param.
                # Force it via the cached_property backing store.
                toolbar = request.toolbar
                toolbar.__dict__["edit_mode_active"] = True
            return request

        @staticmethod
        def create_pages(source, languages):
            """CMS 4.x compatible override: no page.publish() or get_draft_object()."""
            from cms.api import create_page, create_title
            from django.conf import settings

            from app_helper.utils import reload_urls

            pages = OrderedDict()
            has_apphook = False
            for page_data in source:
                main_data = deepcopy(page_data[languages[0]])
                main_data.pop("publish", None)
                main_data.pop("published", None)
                main_data["language"] = languages[0]
                if main_data.get("parent", None):
                    main_data["parent"] = pages[main_data["parent"]]
                page = create_page(**main_data)
                has_apphook = has_apphook or "apphook" in main_data
                for lang in languages[1:]:
                    if lang in page_data:
                        title_data = deepcopy(page_data[lang])
                        title_data.pop("publish", None)
                        title_data.pop("published", None)
                        title_data["language"] = lang
                        title_data["page"] = page
                        create_title(**title_data)
                pages[page.get_slug(languages[0])] = page
            if has_apphook:
                reload_urls(settings, cms_apps=True)
            return list(pages.values())

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
