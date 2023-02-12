from django.contrib.auth import get_user_model
from django.db import migrations

from djangocms_blog.models import Post, PostContent

User = get_user_model()


def move_plugins_to_blog_content(apps, schema_editor):
    """ Adds instances for the new model.
    ATTENTION: All fields of the model must have a valid default value!"""

    versioning_installed = apps.is_installed("djangocms_verisoning")
    if versioning_installed:
        migration_user = User.objects.first()
    else:
        migration_user = None

    for post in Post.objects.all():
        if not post.postcontent_set.exists():
            # Not yet migrated
            for translation in post.translations.all():
                print(f"Copying {translation.language_code} to post content...")
                content = PostContent(
                    language=translation.language_code,
                    title=translation.title,
                    slug=translation.slug,
                    subtitle=translation.subtitle,
                    abstract=translation.abstract,
                    meta_description=translation.meta_description,
                    meta_keywords=translation.meta_keywords,
                    meta_title=translation.meta_title,
                    post_text=translation.post_text,
                    post=post,
                )
                content.save()  # This does not create a Verison object even if versioning is installed
                if versioning_installed:
                    from djangocms_versioning.constants import DRAFT, PUBLISHED
                    from djangocms_versioning.models import Version

                    Version.objects.create(
                        content=content,
                        created_by=migration_user,
                        state=PUBLISHED if post.publish else DRAFT,
                    )
                translation.delete()
                # Move plugins to post content placeholders
                if post.media:
                    media_plugins = post.media.get_plugins().filter(language=translation.language_code)
                    media_plugins.update(placeholder=content.media)
                if post.content:
                    print("Moving content plugins...")
                    content_plugins = post.conent.get_plugins().filter(language=translation.language_code)
                    content_plugins.update(placeholder=content.content)
                if post.liveblog:
                    live_plugins = post.liveblog.get_plugin().filter(language=translation.language_code)
                    live_plugins.update(placeholder=content.liveblog)


def move_plugins_back_to_blog(apps, schema_editor):
    """ Adds instances for the new model.ATTENTION: All fields of the model must have a valid default value!"""
    raise NotImplementedError()


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_blog", "0043_postcontent"),
    ]

    operations = [
        migrations.RunPython(move_plugins_to_blog_content, move_plugins_back_to_blog),
    ]
