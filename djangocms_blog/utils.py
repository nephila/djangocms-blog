from django.apps import apps
from django.conf import settings

_versioning_enabled = None if "djangocms_versioning" in settings.INSTALLED_APPS else False


def is_versioning_enabled():
    global _versioning_enabled

    if _versioning_enabled is None:
        from .models import PostContent

        try:
            app_config = apps.get_app_config("djangocms_versioning")
            _versioning_enabled = app_config.cms_extension.is_content_model_versioned(PostContent)
        except LookupError:
            _versioning_enabled = False
    return _versioning_enabled
