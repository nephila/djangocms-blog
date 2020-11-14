from django.db import migrations, models

from djangocms_blog.models import thumbnail_model


class Migration(migrations.Migration):

    dependencies = [
        ("filer", "0003_thumbnailoption"),
        ("djangocms_blog", "0016_auto_20160502_1741"),
    ]

    operations = []
