# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0023_auto_20160626_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='authorentriesplugin',
            name='template_folder',
            field=models.CharField(default='Default template', verbose_name='Plugin template', max_length=200, help_text='Select plugin template to load for this instance', choices=[('plugins', 'Default template')]),
        ),
        migrations.AddField(
            model_name='genericblogplugin',
            name='template_folder',
            field=models.CharField(default='Default template', verbose_name='Plugin template', max_length=200, help_text='Select plugin template to load for this instance', choices=[('plugins', 'Default template')]),
        ),
        migrations.AddField(
            model_name='latestpostsplugin',
            name='template_folder',
            field=models.CharField(default='Default template', verbose_name='Plugin template', max_length=200, help_text='Select plugin template to load for this instance', choices=[('plugins', 'Default template')]),
        ),
    ]
