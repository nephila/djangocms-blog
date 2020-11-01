import django.db.models.deletion
import filer.fields.image
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0013_urlconfrevision"),
        ("filer", "0003_thumbnailoption"),
    ]

    operations = [
        migrations.CreateModel(
            name="Liveblog",
            fields=[
                (
                    "cmsplugin_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="cms.CMSPlugin",
                        on_delete=django.db.models.deletion.CASCADE,
                    ),
                ),
                ("body", models.TextField(verbose_name="body")),
                ("publish", models.BooleanField(default=False, verbose_name="publish liveblog entry")),
                (
                    "image",
                    filer.fields.image.FilerImageField(
                        related_name="djangocms_blog_liveblog_image",
                        on_delete=django.db.models.deletion.SET_NULL,
                        verbose_name="image",
                        blank=True,
                        to="filer.Image",
                        null=True,
                    ),
                ),
                (
                    "thumbnail",
                    models.ForeignKey(
                        related_name="djangocms_blog_liveblog_thumbnail",
                        on_delete=django.db.models.deletion.SET_NULL,
                        verbose_name="thumbnail size",
                        blank=True,
                        to="filer.ThumbnailOption",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "liveblog entry",
                "verbose_name_plural": "liveblog entries",
            },
            bases=("cms.cmsplugin",),
        ),
    ]
