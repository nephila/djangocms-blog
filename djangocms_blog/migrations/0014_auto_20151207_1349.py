# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangocms_blog.models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0013_auto_20151207_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogcategorytranslation',
            name='slug',
            field=djangocms_blog.models.UnuniqueSlugField(verbose_name='Slug', blank=True),
            preserve_default=True,
        ),
    ]
