# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0005_auto_20150212_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posttranslation',
            name='abstract',
            field=djangocms_text_ckeditor.fields.HTMLField(verbose_name='Abstract', blank=True, default=''),
            preserve_default=True,
        ),
    ]
