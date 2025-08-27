from django.db import migrations

from djangocms_blog.models import HTMLField


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_blog", "0005_auto_20150212_1118"),
    ]

    operations = [
        migrations.AlterField(
            model_name="posttranslation",
            name="abstract",
            field=HTMLField(verbose_name="Abstract", blank=True, default=""),
            preserve_default=True,
        ),
    ]
