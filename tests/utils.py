import contextlib
import os
import shutil
import sys
from distutils.version import LooseVersion
from tempfile import mkdtemp
from unittest.mock import patch

import django
import six
from django.core.management import call_command
from django.urls import clear_url_caches
from django.utils.functional import empty

HELPER_FILE = "helper.py"

try:
    import cms  # NOQA

    CMS = True
    CMS_40 = LooseVersion("4.0") <= LooseVersion(cms.__version__) < LooseVersion("4.1")
    CMS_38 = LooseVersion("3.8") <= LooseVersion(cms.__version__) < LooseVersion("3.9")
    CMS_37 = LooseVersion("3.7") <= LooseVersion(cms.__version__) < LooseVersion("3.8")
    CMS_36 = LooseVersion("3.6") <= LooseVersion(cms.__version__) < LooseVersion("3.7")
    CMS_35 = LooseVersion("3.5") <= LooseVersion(cms.__version__) < LooseVersion("3.6")
    CMS_34 = LooseVersion("3.4") <= LooseVersion(cms.__version__) < LooseVersion("3.5")
    CMS_33 = LooseVersion("3.3") <= LooseVersion(cms.__version__) < LooseVersion("3.4")
    CMS_32 = LooseVersion("3.2") <= LooseVersion(cms.__version__) < LooseVersion("3.3")
    CMS_31 = LooseVersion("3.1") <= LooseVersion(cms.__version__) < LooseVersion("3.2")
    CMS_30 = LooseVersion("3.0") <= LooseVersion(cms.__version__) < LooseVersion("3.1")
except ImportError:  # pragma: no cover
    CMS = False
    CMS_40 = False
    CMS_38 = False
    CMS_37 = False
    CMS_36 = False
    CMS_35 = False
    CMS_34 = False
    CMS_33 = False
    CMS_32 = False
    CMS_31 = False
    CMS_30 = False

DJANGO_2_2 = LooseVersion(django.get_version()) < LooseVersion("3.0")
DJANGO_3_0 = LooseVersion(django.get_version()) < LooseVersion("3.1")
DJANGO_3_1 = LooseVersion(django.get_version()) < LooseVersion("3.2")
DJANGO_3_2 = LooseVersion(django.get_version()) < LooseVersion("4.0")


def load_from_file(module_path):
    """
    Load a python module from its absolute filesystem path

    Borrowed from django-cms
    """
    from imp import PY_SOURCE, load_module

    imported = None
    if module_path:
        with open(module_path) as openfile:
            imported = load_module("mod", openfile, module_path, ("imported", "r", PY_SOURCE))
    return imported


@contextlib.contextmanager
def work_in(dirname=None):
    """
    Context manager version of os.chdir. When exited, returns to the working
    directory prior to entering.

    Grabbed from cookiecutter, thanks audreyr!
    """
    curdir = os.getcwd()
    try:
        if dirname is not None:
            if dirname not in sys.path:
                sys.path.insert(0, dirname)
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


@contextlib.contextmanager
def captured_output():
    with patch("sys.stdout", new_callable=six.StringIO) as out:
        with patch("sys.stderr", new_callable=six.StringIO) as err:
            yield out, err


# Borrowed from django CMS codebase
@contextlib.contextmanager
def temp_dir(suffix="", container="/dev/shm/"):
    name = make_temp_dir(suffix, container)
    yield name
    shutil.rmtree(name)


def make_temp_dir(suffix="", container="/dev/shm/"):
    if os.path.exists(container):
        return mkdtemp(suffix=suffix, dir=container)
    return mkdtemp(suffix=suffix)


@contextlib.contextmanager
def persistent_dir(suffix, container="data"):
    name = os.path.abspath(os.path.join(container, suffix))
    if not os.path.exists(name):
        os.makedirs(name)
    yield name


class DisableMigrations:
    def __contains__(self, item):  # pragma: no cover
        return True

    def __getitem__(self, item):  # pragma: no cover
        return None


def _reset_django(settings):
    """
    Hackish way to reset the django instance settings and AppConfig
    :param settings: django settings module
    """
    if settings._wrapped != empty:
        clear_url_caches()
        from django.apps import apps

        apps.clear_cache()
        settings._wrapped = empty
        clear_url_caches()


def _make_settings(args, application, settings, STATIC_ROOT, MEDIA_ROOT):  # NOQA
    """
    Setup the Django settings
    :param args: docopt arguments
    :param application: application module name
    :param settings: Django settings module
    :param STATIC_ROOT: static root directory
    :param MEDIA_ROOT: media root directory
    :return:
    """
    import dj_database_url

    from .default_settings import get_default_settings

    try:
        extra_settings_file = args.get("--extra-settings")
        if not extra_settings_file:
            extra_settings_file = HELPER_FILE
        if extra_settings_file[-3:] != ".py":  # pragma: no cover
            filename, __ = os.path.splitext(extra_settings_file)
            extra_settings_file = "{}.py".format(filename)
        extra_settings = load_from_file(extra_settings_file).HELPER_SETTINGS
    except (OSError, AttributeError):
        extra_settings = None
    default_name = ":memory:" if args["test"] else "local.sqlite"
    db_url = os.environ.get("DATABASE_URL", "sqlite://localhost/%s" % default_name)
    configs = {
        "DATABASES": {"default": dj_database_url.parse(db_url)},
        "STATIC_ROOT": STATIC_ROOT,
        "MEDIA_ROOT": MEDIA_ROOT,
        "USE_TZ": True,
        "USE_CMS": args["--cms"],
        "BASE_APPLICATION": application,
    }

    if configs["USE_CMS"] or getattr(extra_settings, "USE_CMS", False):
        CMS_APPS = [  # NOQA
            "cms",
            "menus",
            "sekizai",
        ]
        CMS_APP_STYLE = ["djangocms_admin_style"]  # NOQA
        CMS_PROCESSORS = [  # NOQA
            "cms.context_processors.cms_settings",
            "sekizai.context_processors.sekizai",
        ]
        CMS_MIDDLEWARE = [  # NOQA
            "cms.middleware.language.LanguageCookieMiddleware",
            "cms.middleware.user.CurrentUserMiddleware",
            "cms.middleware.page.CurrentPageMiddleware",
            "cms.middleware.toolbar.ToolbarMiddleware",
        ]
        if args["server"]:
            CMS_MIDDLEWARE.append("cms.middleware.utils.ApphookReloadMiddleware")
        URLCONF = "app_helper.urls"  # NOQA
    else:
        CMS_APPS = []  # NOQA
        CMS_APP_STYLE = []  # NOQA
        CMS_MIDDLEWARE = []  # NOQA
        CMS_PROCESSORS = []  # NOQA
        URLCONF = "app_helper.urls"  # NOQA

    default_settings = get_default_settings(
        CMS_APPS, CMS_PROCESSORS, CMS_MIDDLEWARE, CMS_APP_STYLE, URLCONF, application,
    )
    migrate = args.get("--migrate") or not args.get("--no-migrate")
    default_settings.update(configs)

    if extra_settings:
        apps = extra_settings.pop("INSTALLED_APPS", [])
        apps_top = extra_settings.pop("TOP_INSTALLED_APPS", [])
        template_processors = extra_settings.pop("TEMPLATE_CONTEXT_PROCESSORS", [])
        template_loaders = extra_settings.pop("TEMPLATE_LOADERS", [])
        template_dirs = extra_settings.pop("TEMPLATE_DIRS", [])
        middleware = extra_settings.pop("MIDDLEWARE_CLASSES", [])
        middleware_top = extra_settings.pop("TOP_MIDDLEWARE_CLASSES", [])
        default_settings.update(extra_settings)
        for app in apps_top:
            default_settings["INSTALLED_APPS"].insert(0, app)
        default_settings["INSTALLED_APPS"].extend(apps)
        default_settings["TEMPLATE_CONTEXT_PROCESSORS"].extend(template_processors)
        default_settings["TEMPLATE_LOADERS"].extend(template_loaders)
        if "TEMPLATE_DIRS" not in default_settings:
            default_settings["TEMPLATE_DIRS"] = []
        default_settings["TEMPLATE_DIRS"].extend(template_dirs)
        default_settings["MIDDLEWARE_CLASSES"].extend(middleware)
        for middleware in middleware_top:
            default_settings["MIDDLEWARE_CLASSES"].insert(0, middleware)

    if "cms" in default_settings["INSTALLED_APPS"]:
        if "treebeard" not in default_settings["INSTALLED_APPS"]:
            default_settings["INSTALLED_APPS"].append("treebeard")
    if "filer" in default_settings["INSTALLED_APPS"] and "mptt" not in default_settings["INSTALLED_APPS"]:
        default_settings["INSTALLED_APPS"].append("mptt")
    if "filer" in default_settings["INSTALLED_APPS"] and "easy_thumbnails" not in default_settings["INSTALLED_APPS"]:
        default_settings["INSTALLED_APPS"].append("easy_thumbnails")

    default_settings["TEMPLATES"] = [
        {
            "NAME": "django",
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {
                "context_processors": [
                    template_processor.replace("django.core", "django.template")
                    for template_processor in default_settings.pop("TEMPLATE_CONTEXT_PROCESSORS")
                ],
                "loaders": default_settings.pop("TEMPLATE_LOADERS"),
            },
        },
    ]
    if "TEMPLATE_DIRS" in default_settings:
        default_settings["TEMPLATES"][0]["DIRS"] = default_settings.pop("TEMPLATE_DIRS")

    # Support for custom user models
    if "AUTH_USER_MODEL" in os.environ:
        custom_user_app = os.environ["AUTH_USER_MODEL"].rpartition(".")[0]
        custom_user_model = ".".join(os.environ["AUTH_USER_MODEL"].split(".")[-2:])
        if "cms" in default_settings["INSTALLED_APPS"]:
            default_settings["INSTALLED_APPS"].insert(default_settings["INSTALLED_APPS"].index("cms"), custom_user_app)
        else:
            default_settings["INSTALLED_APPS"].insert(
                default_settings["INSTALLED_APPS"].index("django.contrib.auth") + 1, custom_user_app,
            )
        default_settings["AUTH_USER_MODEL"] = custom_user_model

    if args["test"]:
        default_settings["SESSION_ENGINE"] = "django.contrib.sessions.backends.cache"
    if application not in default_settings["INSTALLED_APPS"]:
        default_settings["INSTALLED_APPS"].append(application)

    if not migrate:
        default_settings["MIGRATION_MODULES"] = DisableMigrations()

    if "MIDDLEWARE" not in default_settings:
        default_settings["MIDDLEWARE"] = default_settings["MIDDLEWARE_CLASSES"]
        del default_settings["MIDDLEWARE_CLASSES"]

    _reset_django(settings)
    settings.configure(**default_settings)
    django.setup()
    reload_urls(settings, cms_apps=False)
    return settings


def reload_urls(settings, urlconf=None, cms_apps=True):
    if "cms.urls" in sys.modules:
        six.moves.reload_module(sys.modules["cms.urls"])
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        six.moves.reload_module(sys.modules[urlconf])
    clear_url_caches()
    if cms_apps:
        from cms.appresolver import clear_app_resolvers, get_app_patterns

        clear_app_resolvers()
        get_app_patterns()


def _create_db(migrate_cmd=False):
    call_command("migrate")


def get_user_model():
    from django.contrib.auth import get_user_model

    return get_user_model()


def create_user(
    username, email, password, is_staff=False, is_superuser=False, base_cms_permissions=False, permissions=None,
):
    from django.contrib.auth.models import Permission

    User = get_user_model()  # NOQA

    try:
        if User.USERNAME_FIELD == "email":
            user = User.objects.get(**{User.USERNAME_FIELD: email})
        else:
            user = User.objects.get(**{User.USERNAME_FIELD: username})
    except User.DoesNotExist:
        user = User()

    if User.USERNAME_FIELD != "email":
        setattr(user, User.USERNAME_FIELD, username)

    try:
        user.email = email
    except AttributeError:
        pass
    user.set_password(password)
    if is_superuser:
        user.is_superuser = True
    if is_superuser or is_staff:
        user.is_staff = True
    user.is_active = True
    user.save()
    if user.is_staff and not is_superuser and base_cms_permissions:
        user.user_permissions.add(Permission.objects.get(codename="add_text"))
        user.user_permissions.add(Permission.objects.get(codename="delete_text"))
        user.user_permissions.add(Permission.objects.get(codename="change_text"))
        user.user_permissions.add(Permission.objects.get(codename="publish_page"))

        user.user_permissions.add(Permission.objects.get(codename="add_page"))
        user.user_permissions.add(Permission.objects.get(codename="change_page"))
        user.user_permissions.add(Permission.objects.get(codename="delete_page"))
    if is_staff and not is_superuser and permissions:
        for permission in permissions:
            user.user_permissions.add(Permission.objects.get(codename=permission))
    return user


def get_user_model_labels():
    User = get_user_model()  # NOQA

    user_orm_label = "{}.{}".format(User._meta.app_label, User._meta.object_name)
    user_model_label = "{}.{}".format(User._meta.app_label, User._meta.model_name)
    return user_orm_label, user_model_label


class UserLoginContext:
    def __init__(self, testcase, user, password=None):
        self.testcase = testcase
        self.user = user
        if password is None:
            password = getattr(user, get_user_model().USERNAME_FIELD)
        self.password = password

    def __enter__(self):
        loginok = self.testcase.client.login(
            username=getattr(self.user, get_user_model().USERNAME_FIELD), password=self.password,
        )
        self.testcase.assertTrue(loginok)
        self.testcase._login_context = self

    def __exit__(self, exc, value, tb):
        self.testcase._login_context = None
        self.testcase.client.logout()


def ensure_unicoded_and_unique(args_list, application):
    """
    Iterate over args_list, make it unicode if needed and ensure that there
    are no duplicates.
    Returns list of unicoded arguments in the same order.
    """
    unicoded_args = []
    for argument in args_list:
        argument = argument if not isinstance(argument, str) else argument
        if argument not in unicoded_args or argument == application:
            unicoded_args.append(argument)
    return unicoded_args
