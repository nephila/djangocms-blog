from django.utils.text import slugify as django_slugify

from .settings import get_setting

__all__ = ["slugify"]


def slugify(base):
    return django_slugify(base, allow_unicode=get_setting("UNICODE_SLUGS"))
