from django.db import migrations, models

from djangocms_blog.models import thumbnail_model


class Migration(migrations.Migration):

    if "cmsplugin_filer" not in thumbnail_model:
        dependencies = [
            ("djangocms_blog", "0017_thumbnail_move"),
        ]

        operations = [
            migrations.AddField(
                model_name="post",
                name="main_image_full_new",
                field=models.ForeignKey(
                    related_name="djangocms_blog_post_full",
                    verbose_name="Main image full",
                    blank=True,
                    to=thumbnail_model,
                    null=True,
                    on_delete=models.deletion.SET_NULL,
                ),
            ),
            migrations.AddField(
                model_name="post",
                name="main_image_thumbnail_new",
                field=models.ForeignKey(
                    related_name="djangocms_blog_post_thumbnail",
                    verbose_name="Main image thumbnail",
                    blank=True,
                    to=thumbnail_model,
                    null=True,
                    on_delete=models.deletion.SET_NULL,
                ),
            ),
        ]
    else:
        dependencies = [
            ("filer", "__first__"),
            ("cmsplugin_filer_image", "__first__"),
            ("djangocms_blog", "0017_thumbnail_move"),
        ]

        operations = []
