# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
import filer.fields.image
from django.db import migrations, models
from djangocms_blog.models import thumbnail_model
from filer.settings import FILER_IMAGE_MODEL

ACTUAL_FILER_IMAGE_MODEL = FILER_IMAGE_MODEL or 'filer.Image'


class Migration(migrations.Migration):

    if 'cmsplugin_filer' not in thumbnail_model:
        filer_dependencies = [
            ('filer', '0003_thumbnailoption'),
            ('cmsplugin_filer_image', '0003_mv_thumbnail_option_to_filer_20160119_1720'),
        ]
    else:
        filer_dependencies = [
            ('filer', '__first__'),
            ('cmsplugin_filer_image', '__first__'),
        ]

    dependencies = [
        migrations.swappable_dependency(ACTUAL_FILER_IMAGE_MODEL),
        ('djangocms_blog', '0003_auto_20141201_2252'),
    ] + filer_dependencies

    operations = [
        migrations.AlterField(
            model_name='post',
            name='main_image',
            field=filer.fields.image.FilerImageField(related_name='djangocms_blog_post_image', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Main image', blank=True, to=ACTUAL_FILER_IMAGE_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='main_image_full',
            field=models.ForeignKey(related_name='djangocms_blog_post_full', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Main image full', blank=True, to=thumbnail_model, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='main_image_thumbnail',
            field=models.ForeignKey(related_name='djangocms_blog_post_thumbnail', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Main image thumbnail', blank=True, to=thumbnail_model, null=True),
            preserve_default=True,
        ),
    ]
