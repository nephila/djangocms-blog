from cms.models import Page
from cms.utils.i18n import get_language_list
from django.db import migrations, models


def forwards(apps, schema_editor):
    BlogConfig = apps.get_model("djangocms_blog", "BlogConfig")
    BlogConfigTranslation = apps.get_model("djangocms_blog", "BlogConfigTranslation")
    Post = apps.get_model("djangocms_blog", "Post")
    BlogCategory = apps.get_model("djangocms_blog", "BlogCategory")
    GenericBlogPlugin = apps.get_model("djangocms_blog", "GenericBlogPlugin")
    LatestPostsPlugin = apps.get_model("djangocms_blog", "LatestPostsPlugin")
    AuthorEntriesPlugin = apps.get_model("djangocms_blog", "AuthorEntriesPlugin")
    config = None
    for page in Page.objects.drafts().filter(application_urls="BlogApp"):
        config, created = BlogConfig.objects.get_or_create(namespace=page.application_namespace)
        if not BlogConfigTranslation.objects.exists():
            for lang in get_language_list():
                title = page.get_title(lang)
                translation = BlogConfigTranslation.objects.create(
                    language_code=lang, master_id=config.pk, app_title=title
                )
    if config:
        for model in (Post, BlogCategory, GenericBlogPlugin, LatestPostsPlugin, AuthorEntriesPlugin):
            for item in model.objects.filter(app_config__isnull=True):
                item.app_config = config
                item.save()


def backwards(apps, schema_editor):
    # No need for backward data migration
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0004_auto_20140924_1038"),
        ("djangocms_blog", "0013_auto_20160201_2235"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
