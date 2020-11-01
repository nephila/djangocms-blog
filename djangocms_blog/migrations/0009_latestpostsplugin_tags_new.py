import taggit_autosuggest.managers
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models


def migrate_tags(apps, schema_editor):
    LatestPostsPlugin = apps.get_model("djangocms_blog", "LatestPostsPlugin")
    Tag = apps.get_model("taggit", "Tag")
    TaggedItem = apps.get_model("taggit", "TaggedItem")
    plugin_content_type = ContentType.objects.get_for_model(LatestPostsPlugin)
    for tag in Tag.objects.all():
        for plugin in tag.latestpostsplugin_set.all():
            if not TaggedItem.objects.filter(
                tag=tag, object_id=plugin.pk, content_type_id=plugin_content_type.pk
            ).exists():
                TaggedItem.objects.create(tag=tag, object_id=plugin.pk, content_type_id=plugin_content_type.pk)


def migrate_tags_reverse(apps, schema_editor):
    LatestPostsPlugin = apps.get_model("djangocms_blog", "LatestPostsPlugin")
    Tag = apps.get_model("taggit", "Tag")
    TaggedItem = apps.get_model("taggit", "TaggedItem")
    plugin_content_type = ContentType.objects.get_for_model(LatestPostsPlugin)
    for tagged in TaggedItem.objects.filter(content_type_id=plugin_content_type.pk):
        post = LatestPostsPlugin.objects.get(pk=tagged.object_id)
        post.tags.add(tagged.tag)
        tagged.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "__first__"),
        ("djangocms_blog", "0008_auto_20150814_0831"),
    ]

    operations = [
        migrations.AddField(
            model_name="latestpostsplugin",
            name="tags_new",
            field=taggit_autosuggest.managers.TaggableManager(
                to="taggit.Tag",
                through="taggit.TaggedItem",
                blank=True,
                help_text="Show only the blog articles tagged with chosen tags.",
                verbose_name="filter by tag",
            ),
            preserve_default=True,
        ),
        migrations.RunPython(migrate_tags, migrate_tags_reverse),
        migrations.RemoveField(
            model_name="latestpostsplugin",
            name="tags",
        ),
        migrations.RenameField(
            model_name="latestpostsplugin",
            old_name="tags_new",
            new_name="tags",
        ),
    ]
