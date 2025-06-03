import importlib
import os.path
import sys
import warnings
from collections import OrderedDict
from contextlib import contextmanager
from copy import deepcopy
from io import StringIO
from tempfile import mkdtemp
from unittest.mock import patch

from cms.api import create_page_content
from cms.test_utils.tmpdir import temp_dir
from cms.test_utils.util.context_managers import UserLoginContext
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.handlers.base import BaseHandler
from django.http import SimpleCookie
from django.test import RequestFactory, TestCase, TransactionTestCase
from django.urls import clear_url_caches
from django.utils.functional import SimpleLazyObject
from django.utils.timezone import now


def create_user(
    username,
    email,
    password,
    is_staff=False,
    is_superuser=False,
    is_active=True,
    add_default_permissions=False,
    permissions=None,
):
    """
    Use this method to create users.

    Default permissions on page and text plugin are added if creating a
    non-superuser and `add_default_permissions` is set.

    Set `permissions` parameter to an iterable of permission codes to add
    custom permissios.
    """
    from django.contrib.auth.models import Permission

    User = get_user_model()

    fields = dict(
        email=email or username + "@django-cms.org",
        last_login=now(),
        is_staff=is_staff,
        is_active=is_active,
        is_superuser=is_superuser,
    )

    # Check for special case where email is used as username
    if get_user_model().USERNAME_FIELD != "email":
        fields[get_user_model().USERNAME_FIELD] = username

    user = User(**fields)
    user.set_password(getattr(user, get_user_model().USERNAME_FIELD))
    user.save()
    if is_staff and not is_superuser and add_default_permissions:
        raise NotImplementedError("add_default_permissions is not implemented")
        self._add_default_permissions(user)
    if is_staff and not is_superuser and permissions:
        for permission in permissions:
            user.user_permissions.add(Permission.objects.get(codename=permission))
    return user


@contextmanager
def captured_output():
    with patch("sys.stdout", new_callable=StringIO) as out:
        with patch("sys.stderr", new_callable=StringIO) as err:
            yield out, err


def reload_urls(settings, urlconf=None, cms_apps=True):
    if "cms.urls" in sys.modules:
        importlib.reload(sys.modules["cms.urls"])
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        importlib.reload(sys.modules[urlconf])
    clear_url_caches()
    if cms_apps:
        from cms.appresolver import clear_app_resolvers, get_app_patterns

        clear_app_resolvers()
        get_app_patterns()


class RequestTestCaseMixin:
    """
    Provide methods to get complex request objects.

    Resulting ``request`` has more realistic attributes (i.e.: all the attributes found in a non-test request) than
    the plain :py:class:`django.test.RequestFactory`.
    """

    _login_context = None

    def _prepare_request(self, request, page, user, lang, use_middlewares, use_toolbar=False, secure=False):
        from importlib import import_module

        from django.contrib.auth.models import AnonymousUser

        engine = import_module(settings.SESSION_ENGINE)

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
        # Let's use middleware in case requested, otherwise just use CMS toolbar if needed
        if use_middlewares:
            self._apply_middlewares(request)
        elif use_toolbar:
            from cms.middleware.toolbar import ToolbarMiddleware

            mid = ToolbarMiddleware(get_response=lambda x: x)
            mid.process_request(request)
        return request

    def _apply_middlewares(self, request):
        handler = BaseHandler()
        from django.utils.module_loading import import_string

        for middleware_path in reversed(settings.MIDDLEWARE):
            middleware = import_string(middleware_path)
            mw_instance = middleware(handler)
            if hasattr(mw_instance, "process_request"):
                mw_instance.process_request(request)

    def login_user_context(self, user, password=None):
        """
        Context manager to make logged in requests.

        Usage::

            with self.login_user_context("<username>", password="<password>"):
                request = self.request("/", lang="en")
                ... # this request has <username> as user

        :param user: user username
        :param password: user password (if omitted, username is used)
        """
        return UserLoginContext(self, user)

    def request(
        self,
        path,
        method="get",
        data=None,
        page=None,
        lang="",
        user=None,
        use_middlewares=False,
        secure=False,
        use_toolbar=False,
    ):
        """
        Create a request for the given parameters.

        Request will be enriched with:

        * session
        * cookies
        * user (Anonymous if :param:user is `None`)
        * django CMS toolbar (is set)
        * current_page (if provided)

        :param path: request path
        :type path: str
        :param method: HTTP verb to use
        :type method: str
        :param data: payload to pass to the underlying :py:class:`django.test.RequestFactory` method
        :type data: dict
        :param page: current page object
        :type page: cms.models.Page
        :param lang: request language
        :type lang: str
        :param user: current user
        :type user: :py:class:`django.contrib.auth.models.AbstractUser`
        :param use_middlewares: pass the request through configured middlewares
        :type use_middlewares: bool
        :param secure: create HTTPS request
        :type secure: bool
        :param use_toolbar: add django CMS toolbar
        :type secure: bool
        :return: request
        """
        request = getattr(RequestFactory(), method)(path, data=data, secure=secure)
        return self._prepare_request(
            request,
            page,
            user,
            lang,
            use_middlewares,
            secure=secure,
            use_toolbar=use_toolbar,
        )


class CreateTestDataMixin:
    """Provide methods to automatically create users on test setup and shortcut to generate test data."""

    user = None
    user_staff = None
    user_normal = None
    site_1 = None
    image_name = "test_image.jpg"

    #: Username for auto-generated superuser
    _admin_user_username = "admin"
    #: Password for auto-generated superuser
    _admin_user_password = "admin"
    #: Email for auto-generated superuser
    _admin_user_email = "admin@admin.com"

    #: Username for auto-generated staff user
    _staff_user_username = "staff"
    #: Password for auto-generated staff user
    _staff_user_password = "staff"
    #: Email for auto-generated staff user
    _staff_user_email = "staff@admin.com"

    #: Username for auto-generated non-staff user
    _user_user_username = "normal"
    #: Password for auto-generated non-staff user
    _user_user_password = "normal"
    #: Email for auto-generated non-staff user
    _user_user_email = "user@admin.com"

    @classmethod
    def _setup_users(cls):
        """
        Create standard users.

        * :py:attr:`user`: superuser
        * :py:attr:`user_staff`: staff user
        * :py:attr:`user_normal`: plain django user
        """
        cls.user = create_user(
            cls._admin_user_username,
            cls._admin_user_email,
            cls._admin_user_password,
            is_staff=True,
            is_superuser=True,
        )
        cls.user_staff = create_user(
            cls._staff_user_username,
            cls._staff_user_email,
            cls._staff_user_password,
            is_staff=True,
            is_superuser=False,
        )
        cls.user_normal = create_user(
            cls._user_user_username,
            cls._user_user_email,
            cls._user_user_password,
            is_staff=False,
            is_superuser=False,
        )

    @classmethod
    def _teardown_users(cls):
        """Delete existing users."""
        User = get_user_model()  # NOQA
        User.objects.all().delete()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._teardown_users()

    def create_user(
        self,
        username,
        email,
        password,
        is_staff=False,
        is_superuser=False,
        base_cms_permissions=False,
        permissions=None,
    ):
        """
        Creates a user with the given properties

        :param username: Username
        :param email: Email
        :param password: password
        :param is_staff: Staff status
        :param is_superuser: Superuser status
        :param base_cms_permissions: Base django CMS permissions
        :param permissions: Other permissions
        :return: User instance
        """
        return create_user(username, email, password, is_staff, is_superuser, base_cms_permissions, permissions)

    @staticmethod
    def create_image(mode="RGB", size=(800, 600)):
        """
        Create a random image suitable for saving as DjangoFile
        :param mode: color mode
        :param size: tuple of width, height
        :return: image object

        It requires Pillow installed in the environment to work

        """
        from PIL import Image as PilImage, ImageDraw

        image = PilImage.new(mode, size)
        draw = ImageDraw.Draw(image)
        x_bit, y_bit = size[0] // 10, size[1] // 10
        draw.rectangle((x_bit, y_bit * 2, x_bit * 7, y_bit * 3), "red")
        draw.rectangle((x_bit * 2, y_bit, x_bit * 3, y_bit * 8), "red")
        return image

    def create_django_image_obj(self):  # pragma: no cover
        return self.create_django_image_object()

    def create_django_image_object(self):
        """
        Create a django image file object suitable for FileField
        It also sets the following attributes:

        * ``self.image_name``: the image base name
        * ``self.filename``: the complete image path

        :return: django file object

        It requires Pillow installed in the environment to work

        """
        img_obj, self.filename = self.create_django_image()
        self.image_name = img_obj.name
        return img_obj

    @classmethod
    def create_django_image(cls):
        """
        Create a django image file object suitable for FileField
        It also sets the following attributes:

        * ``self.image_name``: the image base name
        * ``self.filename``: the complete image path

        :return: (django file object, path to file image)

        It requires Pillow installed in the environment to work
        """
        from django.core.files import File as DjangoFile

        img = cls.create_image()
        image_name = "test_file.jpg"
        if settings.FILE_UPLOAD_TEMP_DIR:
            tmp_dir = settings.FILE_UPLOAD_TEMP_DIR
        else:
            tmp_dir = mkdtemp()
        filename = os.path.join(tmp_dir, image_name)
        img.save(filename, "JPEG")
        return DjangoFile(open(filename, "rb"), name=image_name), filename

    def create_filer_image_object(self):
        """
        Create a filer image object suitable for FilerImageField
        It also sets the following attributes:

        * ``self.image_name``: the image base name
        * ``self.filename``: the complete image path
        * ``self.filer_image``: the filer image object

        :return: filer image object

        It requires Pillow and django-filer installed in the environment to work

        """
        self.filer_image = self.create_filer_image(self.user, self.image_name)
        return self.filer_image

    @classmethod
    def create_filer_image(cls, user, image_name):
        """
        Create a filer image object suitable for FilerImageField
        It also sets the following attributes:

        * ``self.image_name``: the image base name
        * ``self.filename``: the complete image path
        * ``self.filer_image``: the filer image object

        :param user: image owner
        :param image_name: image name
        :return: filer image object

        It requires Pillow and django-filer installed in the environment to work

        """
        from filer.models import Image

        file_obj, filename = cls.create_django_image()
        filer_image = Image.objects.create(owner=user, file=file_obj, original_filename=image_name)
        return filer_image


class CMSPageRenderingMixin(RequestTestCaseMixin):
    """
    Provide hooks to create sample pages in tests and helper methods to render pages and plugins.
    """

    languages = None

    _pages_data = ()
    """
    List of pages data for the different languages.

    Each item of the list is a dictionary containing the attributes
    (as accepted by :py:func:`cms.api.create_page`) of the page to be created.

    The first language will be created with :py:func:`cms.api.create_page` the following
    languages using :py:func:`cms.api.create_title`.

    Example:
        Single page created in en, fr, it languages::

            _pages_data = (
                {
                    'en': {'title': 'Page title', 'template': 'page.html', 'publish': True},
                    'fr': {'title': 'Titre', 'publish': True},
                    'it': {'title': 'Titolo pagina', 'publish': False}
                },
            )

    """

    @classmethod
    def _setup_cms(cls):
        """
        Setup data required by django CMS as class attributes.

        * :py:attr:`site_1`: instance of the first :py:class:`~django.contrib.sites.models.Site`
        * :py:attr:`languages`: list of configured languages
        """
        from django.contrib.sites.models import Site

        cls.site_1 = Site.objects.all().first()

        try:
            from cms.utils import get_language_list

            cls.languages = get_language_list()
        except ImportError:
            cls.languages = [x[0] for x in settings.LANGUAGES]

    def get_pages_data(self):
        """
        Construct a list of pages in the different languages available for the
        project. Default implementation is to return the :py:attr:`_pages_data`
        attribute

        :return: list of pages data
        """
        return self._pages_data

    def get_pages(self):
        """
        Create pages using self._pages_data and self.languages

        :return: list of created pages
        """
        return self.create_pages(self._pages_data, self.languages)

    @staticmethod
    def create_pages(source, languages):
        """
        Build pages according to the pages data provided by :py:meth:`get_pages_data`
        and returns the list of the draft version of each
        """
        from cms.api import create_page

        pages = OrderedDict()
        has_apphook = False
        home_set = False
        for page_data in source:
            main_data = deepcopy(page_data[languages[0]])
            main_data["language"] = languages[0]
            if main_data.get("parent", None):
                main_data["parent"] = pages[main_data["parent"]]
            main_data.pop("publish")
            page = create_page(**main_data)
            has_apphook = has_apphook or "apphook" in main_data
            for lang in languages[1:]:
                if lang in page_data:
                    content_data = deepcopy(page_data[lang])
                    content_data["language"] = lang
                    content_data["page"] = page
                    content_data.pop("publish")
                    create_page_content(**content_data)
            if not home_set and hasattr(page, "set_as_homepage") and main_data.get("published", False):
                page.set_as_homepage()
                home_set = True
            # page = page.get_draft_object()
            pages[page.get_slug(languages[0])] = page
        if has_apphook:
            reload_urls(settings, cms_apps=True)
        return list(pages.values())

    def get_content_renderer(self, request):
        """
        Returns a the plugin renderer. Only for django CMS 3.4+

        :param request: request instance
        :return: ContentRenderer instance
        """
        from cms.plugin_rendering import ContentRenderer

        return ContentRenderer(request)

    def get_plugin_context(self, page, lang, plugin, edit=False):
        """
        Returns a context suitable for CMSPlugin.render_plugin / render_placeholder

        :param page: Page object
        :param lang: Current language
        :param plugin: Plugin instance
        :param edit: Enable edit mode for rendering
        :return: PluginContext instance
        """
        from cms.plugin_rendering import PluginContext
        from sekizai.context_processors import sekizai

        request = self.get_toolbar_request(page, self.user, lang=lang, edit=edit)
        context = {"request": request}
        renderer = self.get_content_renderer(request)
        if renderer:
            context["cms_content_renderer"] = renderer
        context.update(sekizai(request))
        return PluginContext(context, plugin, plugin.placeholder)

    def render_plugin(self, page, lang, plugin, edit=False):
        """
        Renders a single plugin using CMSPlugin.render_plugin

        :param page: Page object
        :param lang: Current language
        :param plugin: Plugin instance
        :param edit: Enable edit mode for rendering
        :return: Rendered plugin
        """
        context = self.get_plugin_context(page, lang, plugin, edit)
        content_renderer = context["cms_content_renderer"]
        rendered = content_renderer.render_plugin(instance=plugin, context=context, placeholder=plugin.placeholder)
        return rendered

    def get_toolbar_request(self, page, user, path=None, edit=False, lang="en", use_middlewares=False, secure=False):
        """
        Create a GET request for the given page suitable for use the django CMS toolbar.

        This method requires django CMS installed to work. It will raise an ImportError otherwise; not a big deal
        as this method makes sense only in a django CMS environment.

        :param page: current page object
        :param user: current user
        :param path: path (if different from the current page path)
        :param edit: whether enabling editing mode
        :param lang: request language
        :param use_middlewares: pass the request through configured middlewares.
        :param secure: create HTTPS request
        :return: request
        """
        from cms.utils.conf import get_cms_setting

        edit_on = get_cms_setting("TOOLBAR_URL__ENABLE")
        path = path or page and page.get_absolute_url(lang)
        if edit:
            path = "{}?{}".format(path, edit_on)

        request = RequestFactory().get(path, secure=secure)
        return self._prepare_request(request, page, user, lang, use_middlewares, use_toolbar=True, secure=secure)

    def get_request(self, page, lang, user=None, path=None, use_middlewares=False, secure=False, use_toolbar=False):
        """
        Create a GET request for the given page and language.

        :param page: current page object
        :param lang: request language
        :param user: current user
        :param path: path (if different from the current page path)
        :param use_middlewares: pass the request through configured middlewares.
        :param secure: create HTTPS request
        :param use_toolbar: add django CMS toolbar
        :return: request
        """
        path = path or page and page.get_absolute_url(lang)
        return self.request(
            path,
            method="get",
            data={},
            page=page,
            lang=lang,
            user=user,
            use_middlewares=use_middlewares,
            secure=secure,
            use_toolbar=use_toolbar,
        )

    def post_request(
        self,
        page,
        lang,
        data,
        user=None,
        path=None,
        use_middlewares=False,
        secure=False,
        use_toolbar=False,
    ):
        """
        Create a POST request for the given page and language with CSRF disabled.

        :param page: current page object
        :param lang: request language
        :param data: POST payload
        :param user: current user
        :param path: path (if different from the current page path)
        :param use_middlewares: pass the request through configured middlewares.
        :param secure: create HTTPS request
        :param use_toolbar: add django CMS toolbar
        :return: request
        """
        path = path or page and page.get_absolute_url(lang)
        return self.request(
            path,
            method="post",
            data=data,
            page=page,
            lang=lang,
            user=user,
            use_middlewares=use_middlewares,
            secure=secure,
            use_toolbar=use_toolbar,
        )


class GenericHelpersMixin:
    def temp_dir(self):
        """
        Return the context manager of a temporary directory that is removed upon exit.

        Usage::

            with self.temp_dir() as temp_path:
                test_file = os.path.join(temp_path, "afile")
                ... # do something with test_file
            ... # test_file and containing directory is removed
        """
        return temp_dir()

    def reload_model(self, obj):
        """
        Reload models instance from database.

        Contrary to ``refresh_from_db`` returns a completely new instance, instead of updating the current one.

        :param obj: model instance to reload
        :return: the reloaded model instance
        """
        return obj.__class__.objects.get(pk=obj.pk)

    @staticmethod
    def reload_urlconf(urlconf=None):
        """Reload django urlconf and any attached apphook."""
        reload_urls(settings, urlconf)

    @contextmanager
    def captured_output(self):
        """
        Context manager that patches stdout / stderr with StringIO and return the instances.

        Useful to test output.

        :return: stdout, stderr wrappers
        """
        with patch("sys.stdout", new_callable=StringIO) as out, patch("sys.stderr", new_callable=StringIO) as err:
            yield out, err


class BaseNoDataTestCaseMixin(CreateTestDataMixin, CMSPageRenderingMixin, GenericHelpersMixin):
    """
    Provide helper methods to setup and interact with Django testing framework.

    Does not create in :py:meth:`setUpClass`, but provides all the methods to tap into automatic data generation.

    Implements:

    * :py:class:`CreateTestDataMixin`
    * :py:class:`CMSPageRenderingMixin`
    * :py:class:`GenericHelpersMixin`
    """


class BaseTestCaseMixin(BaseNoDataTestCaseMixin):
    """
    Provide helper methods to setup and interact with Django testing framework.

    Like :py:class:`BaseNoDataTestCaseMixin` but create sample data in :py:meth:`setUpClass`
    according to :py:class:`CreateTestDataMixin` and :py:class:`CMSPageRenderingMixin` configuration

    Implements:

    * :py:class:`CreateTestDataMixin`
    * :py:class:`CMSPageRenderingMixin`
    * :py:class:`GenericHelpersMixin`
    """

    @classmethod
    def setUpClass(cls):
        cls._setup_cms()
        cls._setup_users()
        super().setUpClass()


class BaseTestCase(BaseTestCaseMixin, TestCase):
    """
    Base class that implements :py:class:`BaseTestCaseMixin` and
    :py:class:`django.tests.TestCase`
    """


class BaseTransactionTestCase(BaseTestCaseMixin, TransactionTestCase):
    """
    Base class that implements :py:class:`BaseTestCaseMixin` and
    :py:class:`django.tests.TransactionTestCase`
    """
