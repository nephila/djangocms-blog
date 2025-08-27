from cms.app_base import CMSAppConfig
from cms.models import Placeholder, PlaceholderRelationField
from django.apps import apps
from django.conf import settings

from .models import PostContent
from .views import ToolbarDetailView

djangocms_versioning_installed = apps.is_installed("djangocms_versioning")


def copy_placeholder_content(original_content):
    """Copy the content object and deepcopy its placeholders and plugins.The PlaceholderRelationField needs to
    be named "placeholders".

    This is needed for versioning integration.
    """
    ContentModel = original_content.__class__
    # Copy content object
    content_fields = {
        field.name: getattr(original_content, field.name)
        for field in ContentModel._meta.fields
        # don't copy primary key because we're creating a new obj
        if ContentModel._meta.pk.name != field.name
    }
    # Use original manager to not create a new Version object here
    new_content = ContentModel._original_manager.create(**content_fields)

    for field in ContentModel._meta.private_fields:
        # Copy PlaceholderRelationFields
        if isinstance(field, PlaceholderRelationField):
            # Copy placeholders
            new_placeholders = []
            for placeholder in getattr(original_content, field.name).all():
                placeholder_fields = {
                    field.name: getattr(placeholder, field.name)
                    for field in Placeholder._meta.fields
                    # don't copy primary key because we're creating a new obj
                    # and handle the source field later
                    if field.name not in [Placeholder._meta.pk.name, "source"]
                }
                if placeholder.source:
                    placeholder_fields["source"] = new_content
                new_placeholder = Placeholder.objects.create(**placeholder_fields)
                # Copy plugins
                placeholder.copy_plugins(new_placeholder)
                new_placeholders.append(new_placeholder)
            getattr(new_content, field.name).add(*new_placeholders)

    return new_content


class BlogCMSConfig(CMSAppConfig):
    cms_enabled = True
    cms_toolbar_enabled_models = [(PostContent, ToolbarDetailView.as_view())]
    djangocms_versioning_enabled = (
        getattr(settings, "VERSIONING_BLOG_MODELS_ENABLED", True) and djangocms_versioning_installed
    )

    if djangocms_versioning_enabled:
        from cms.utils.i18n import get_language_tuple
        from djangocms_versioning.datastructures import VersionableItem

        versioning = [
            VersionableItem(
                content_model=PostContent,
                grouper_field_name="post",
                extra_grouping_fields=["language"],
                version_list_filter_lookups={"language": get_language_tuple},
                copy_function=copy_placeholder_content,
                grouper_selector_option_label=lambda obj, lang: obj.get_title(lang),
            ),
        ]
