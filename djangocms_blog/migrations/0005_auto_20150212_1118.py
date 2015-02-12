# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0004_auto_20150108_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=cms.models.fields.PlaceholderField(slotname='post_content', to='cms.Placeholder', null=True, related_name='post_content', editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='enable_comments',
            field=models.BooleanField(default=False, verbose_name='Enable comments on post'),
            preserve_default=True,
        ),
    ]
