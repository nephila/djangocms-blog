# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
import django.utils.timezone
import djangocms_text_ckeditor.fields
import filer.fields.image
from django.conf import settings
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
        ('djangocms_blog', '0006_auto_20150214_1907'),
        migrations.swappable_dependency(ACTUAL_FILER_IMAGE_MODEL),
    ] + filer_dependencies

    operations = [
        migrations.AlterModelOptions(
            name='blogcategorytranslation',
            options={'managed': True, 'verbose_name': 'blog category Translation', 'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='posttranslation',
            options={'managed': True, 'verbose_name': 'blog article Translation', 'default_permissions': ()},
        ),
        migrations.AlterField(
            model_name='authorentriesplugin',
            name='authors',
            field=models.ManyToManyField(verbose_name='authors', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='authorentriesplugin',
            name='latest_posts',
            field=models.IntegerField(help_text='The number of author articles to be displayed.', verbose_name='articles', default=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blogcategorytranslation',
            name='language_code',
            field=models.CharField(db_index=True, verbose_name='Language', max_length=15),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='latestpostsplugin',
            name='categories',
            field=models.ManyToManyField(blank=True, help_text='Show only the blog articles tagged with chosen categories.', verbose_name='filter by category', to='djangocms_blog.BlogCategory'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='latestpostsplugin',
            name='latest_posts',
            field=models.IntegerField(help_text='The number of latests articles to be displayed.', verbose_name='articles', default=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='latestpostsplugin',
            name='tags',
            field=models.ManyToManyField(blank=True, help_text='Show only the blog articles tagged with chosen tags.', verbose_name='filter by tag', to='taggit.Tag'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(blank=True, verbose_name='author', to=settings.AUTH_USER_MODEL, related_name='djangocms_blog_post_author', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='last modified'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='date_published',
            field=models.DateTimeField(verbose_name='published Since', default=django.utils.timezone.now),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='date_published_end',
            field=models.DateTimeField(blank=True, verbose_name='published Until', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='enable_comments',
            field=models.BooleanField(verbose_name='enable comments on post', default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='main_image',
            field=filer.fields.image.FilerImageField(on_delete=django.db.models.deletion.SET_NULL, blank=True, verbose_name='main image', to=ACTUAL_FILER_IMAGE_MODEL, related_name='djangocms_blog_post_image', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='main_image_full',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, verbose_name='main image full', to=thumbnail_model, related_name='djangocms_blog_post_full', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='main_image_thumbnail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, verbose_name='main image thumbnail', to=thumbnail_model, related_name='djangocms_blog_post_thumbnail', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='publish',
            field=models.BooleanField(verbose_name='publish', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='abstract',
            field=djangocms_text_ckeditor.fields.HTMLField(verbose_name='abstract'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='language_code',
            field=models.CharField(db_index=True, verbose_name='Language', max_length=15),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='meta_description',
            field=models.TextField(blank=True, verbose_name='post meta description', default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='meta_keywords',
            field=models.TextField(blank=True, verbose_name='post meta keywords', default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='meta_title',
            field=models.CharField(blank=True, help_text='used in title tag and social sharing', verbose_name='post meta title', max_length=255, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='post_text',
            field=djangocms_text_ckeditor.fields.HTMLField(blank=True, verbose_name='text', default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='title',
            field=models.CharField(verbose_name='title', max_length=255),
            preserve_default=True,
        ),
    ]
