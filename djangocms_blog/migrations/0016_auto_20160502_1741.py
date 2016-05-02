# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0015_auto_20160408_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogcategorytranslation',
            name='slug',
            field=models.SlugField(max_length=255, verbose_name='slug', blank=True),
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='slug',
            field=models.SlugField(max_length=255, verbose_name='slug', blank=True),
        ),
    ]
