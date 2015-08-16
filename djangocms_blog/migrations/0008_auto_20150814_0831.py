# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0007_auto_20150719_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posttranslation',
            name='abstract',
            field=djangocms_text_ckeditor.fields.HTMLField(default=b'', verbose_name='abstract', blank=True),
            preserve_default=True,
        ),
    ]
