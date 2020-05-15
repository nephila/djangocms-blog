import djangocms_text_ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_blog", "0005_auto_20150212_1118"),
    ]

    operations = [
        migrations.AlterField(
            model_name="posttranslation",
            name="abstract",
            field=djangocms_text_ckeditor.fields.HTMLField(verbose_name="Abstract", blank=True, default=""),
            preserve_default=True,
        ),
    ]
