from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangocms_blog", "0011_auto_20151024_1809"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="blogconfig",
            options={"verbose_name": "blog config", "verbose_name_plural": "blog configs"},
        ),
    ]
