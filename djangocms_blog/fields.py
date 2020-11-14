from django.utils.text import slugify as django_slugify

__all__ = ["slugify"]


def slugify(base):
    return django_slugify(base, allow_unicode=True)
