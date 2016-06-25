# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from djangocms_blog.models import thumbnail_model


class Migration(migrations.Migration):

    if 'cmsplugin_filer' not in thumbnail_model:
        dependencies = [
            ('djangocms_blog', '0019_thumbnail_move3'),
            ('filer', '0003_thumbnailoption'),
            ('cmsplugin_filer_image', '0003_mv_thumbnail_option_to_filer_20160119_1720'),
        ]
        run_before = [
            ('cmsplugin_filer_image', '0004_auto_20160120_0950'),
        ]

        operations = [
            migrations.RemoveField(
                model_name='post',
                name='main_image_full'
            ),
            migrations.RemoveField(
                model_name='post',
                name='main_image_thumbnail',
            ),
            migrations.RenameField(
                model_name='post',
                old_name='main_image_full_new',
                new_name='main_image_full',
            ),
            migrations.RenameField(
                model_name='post',
                old_name='main_image_thumbnail_new',
                new_name='main_image_thumbnail',
            )
        ]
    else:
        dependencies = [
            ('filer', '__first__'),
            ('cmsplugin_filer_image', '__first__'),
            ('djangocms_blog', '0019_thumbnail_move3'),
        ]

        operations = []
