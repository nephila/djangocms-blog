# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.image
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0003_auto_20141201_2252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='main_image',
            field=filer.fields.image.FilerImageField(related_name='djangocms_blog_post_image', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Main image', blank=True, to='filer.Image', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='main_image_full',
            field=models.ForeignKey(related_name='djangocms_blog_post_full', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Main image full', blank=True, to='cmsplugin_filer_image.ThumbnailOption', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='main_image_thumbnail',
            field=models.ForeignKey(related_name='djangocms_blog_post_thumbnail', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Main image thumbnail', blank=True, to='cmsplugin_filer_image.ThumbnailOption', null=True),
            preserve_default=True,
        ),
    ]
