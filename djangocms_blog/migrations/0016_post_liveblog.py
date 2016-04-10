# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('djangocms_blog', '0015_auto_20160408_1849'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='liveblog',
            field=cms.models.fields.PlaceholderField(related_name='live_blog', slotname='live_blog', editable=False, to='cms.Placeholder', null=True),
        ),
    ]
