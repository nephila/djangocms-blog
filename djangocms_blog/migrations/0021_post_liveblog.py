# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '__first__'),
        ('djangocms_blog', '0020_thumbnail_move4'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='liveblog',
            field=cms.models.fields.PlaceholderField(related_name='live_blog', slotname='live_blog', editable=False, to='cms.Placeholder', null=True),
        ),
    ]
