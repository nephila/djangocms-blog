from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_blog", "0032_auto_20180109_0023"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blogcategorytranslation",
            name="meta_description",
            field=models.TextField(blank=True, verbose_name="category meta description", default=""),
        ),
    ]
