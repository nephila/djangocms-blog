# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('djangocms_blog', '0009_latestpostsplugin_tags_new'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blogcategorytranslation',
            options={'default_permissions': (), 'verbose_name': 'Category Translation'},
        ),
        migrations.AlterModelOptions(
            name='posttranslation',
            options={'default_permissions': (), 'verbose_name': 'News Translation'},
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='sites',
            field=models.ManyToManyField(help_text='Select sites in which to show the category. If none is set it will be visible in all the configured sites.', blank=True, null=True, to='sites.Site', verbose_name='Site(s)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='authorentriesplugin',
            name='authors',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Authors'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blogcategorytranslation',
            name='language_code',
            field=models.CharField(max_length=15, choices=[('sv', 'Svenska')], verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='enable_comments',
            field=models.BooleanField(default=False, verbose_name='enable comments on post'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='abstract',
            field=djangocms_text_ckeditor.fields.HTMLField(default='', blank=True, verbose_name='abstract'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='language_code',
            field=models.CharField(max_length=15, choices=[('sv', 'Svenska')], verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
    ]
