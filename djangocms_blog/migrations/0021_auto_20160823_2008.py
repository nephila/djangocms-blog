# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from djangocms_blog.models import thumbnail_model


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0020_thumbnail_move4'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorentriesplugin',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='djangocms_blog_authorentriesplugin', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='genericblogplugin',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='djangocms_blog_genericblogplugin', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='latestpostsplugin',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='djangocms_blog_latestpostsplugin', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='post',
            name='main_image_full',
            field=models.ForeignKey(related_name='djangocms_blog_post_full', on_delete=django.db.models.deletion.SET_NULL, verbose_name='main image full', blank=True, to=thumbnail_model, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='main_image_thumbnail',
            field=models.ForeignKey(related_name='djangocms_blog_post_thumbnail', on_delete=django.db.models.deletion.SET_NULL, verbose_name='main image thumbnail', blank=True, to=thumbnail_model, null=True),
        ),
    ]
