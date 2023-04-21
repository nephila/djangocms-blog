import cms.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0020_old_tree_cleanup"),
        ("djangocms_blog", "0020_thumbnail_move4"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="liveblog",
            field=cms.models.fields.PlaceholderField(
                related_name="live_blog", slotname="live_blog", editable=False, to="cms.Placeholder", null=True
            ),
        ),
    ]
