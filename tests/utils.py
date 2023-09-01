import contextlib
import os
import shutil
import sys
from tempfile import mkdtemp
from unittest.mock import patch

import django
import six
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.urls import clear_url_caches

from packaging.version import Version

try:
    import cms  # NOQA

    CMS = True
    CMS_41 = Version("4.1") <= Version(cms.__version__) < Version("4.0")
    CMS_40 = Version("4.0") <= Version(cms.__version__) < Version("4.1")
except ImportError:  # pragma: no cover
    CMS = False
    CMS_41 = False
    CMS_40 = False


DJANGO_3_2 = Version(django.get_version()) < Version("4.0")

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
    username,
    email,
    password,
    is_staff=False,
    is_superuser=False,
    base_cms_permissions=False,
    permissions=None,
):
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
            username=getattr(self.user, get_user_model().USERNAME_FIELD),
            password=self.password,
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
