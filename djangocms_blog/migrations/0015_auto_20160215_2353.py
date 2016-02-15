# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0014_auto_20160215_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='posttranslation',
            name='gplus_description',
            field=models.TextField(verbose_name='google+ description', blank=True, default=''),
        ),
        migrations.AddField(
            model_name='posttranslation',
            name='og_description',
            field=models.TextField(verbose_name='OpenGraph description', blank=True, default=''),
        ),
        migrations.AddField(
            model_name='posttranslation',
            name='twitter_description',
            field=models.CharField(verbose_name='twitter description', max_length=255, blank=True, default=''),
        ),
    ]
