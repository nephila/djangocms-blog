# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models.fields
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0004_auto_20150108_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=cms.models.fields.PlaceholderField(to='cms.Placeholder', slotname='post_content', editable=False, related_name='post_content', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='enable_comments',
            field=models.BooleanField(default=False, verbose_name='Enable comments on post'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='meta_description',
            field=models.TextField(default='', verbose_name='Post meta description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='meta_keywords',
            field=models.TextField(default='', verbose_name='Post meta keywords', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='meta_title',
            field=models.CharField(help_text='used in title tag and social sharing', max_length=255, verbose_name='Post meta title', blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='post_text',
            field=djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='Text', blank=True),
            preserve_default=True,
        ),
    ]
