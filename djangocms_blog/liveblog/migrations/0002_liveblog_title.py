from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("liveblog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="liveblog",
            name="title",
            field=models.CharField(default="", max_length=255, verbose_name="title"),
            preserve_default=False,
        ),
    ]
