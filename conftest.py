import os

import django

from django.conf import settings
from tests import settings as test_settings


def pytest_configure():
    """Setup Django settings"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    # get all all-upercase settings from test_settings
    settings_dict = {key: getattr(test_settings, key) for key in test_settings.__dir__() if key.isupper()}

    settings.configure(**settings_dict)
    django.setup()
    djang
