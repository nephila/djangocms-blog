from django.db import migrations, models

from djangocms_blog.models import thumbnail_model


def move_thumbnail_opt_to_filer(apps, schema_editor):
    Post = apps.get_model("djangocms_blog", "Post")
    for post in Post.objects.all():
        post.main_image_full_new_id = post.main_image_full_id
        post.main_image_thumbnail_new_id = post.main_image_thumbnail_id
        post.save()


def move_thumbnail_opt_to_plugin(apps, schema_editor):
    Post = apps.get_model("djangocms_blog", "Post")
    for post in Post.objects.all():
        post.main_image_full_id = post.main_image_full_new_id
        post.main_image_thumbnail_id = post.main_image_thumbnail_new_id
        post.save()


class Migration(migrations.Migration):
    if "cmsplugin_filer" not in thumbnail_model:
        dependencies = [
            ("djangocms_blog", "0018_thumbnail_move2"),
        ]

        operations = [
            migrations.RunPython(move_thumbnail_opt_to_filer, move_thumbnail_opt_to_plugin),
        ]
    else:
        dependencies = [
            ("filer", "__first__"),
            ("cmsplugin_filer_image", "__first__"),
            ("djangocms_blog", "0018_thumbnail_move2"),
        ]

        operations = []
