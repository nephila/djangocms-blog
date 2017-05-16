# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-18 06:51
from __future__ import unicode_literals

import cms.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('djangocms_blog', '0027_auto_20160917_0123'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_common_bottom',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_common_bottom', slotname='blog_common_bottom', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_common_footer',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_common_footer', slotname='blog_common_footer', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_common_header',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_common_header', slotname='blog_common_header', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_common_sidebar',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_common_sidebar', slotname='blog_common_sidebar', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_common_top',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_common_top', slotname='blog_common_top', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_detail_bottom',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_detail_bottom', slotname='blog_detail_bottom', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_detail_footer',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_detail_footer', slotname='blog_detail_footer', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_detail_header',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_detail_header', slotname='blog_detail_header', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_detail_sidebar',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_detail_sidebar', slotname='blog_detail_sidebar', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_detail_top',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_detail_top', slotname='blog_detail_top', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_list_bottom',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_list_bottom', slotname='blog_list_bottom', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_list_footer',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_list_footer', slotname='blog_list_footer', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_list_header',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_list_header', slotname='blog_list_header', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_list_sidebar',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_list_sidebar', slotname='blog_list_sidebar', to='cms.Placeholder'),
        ),
        migrations.AddField(
            model_name='blogconfig',
            name='placeholder_list_top',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djangocms_blog_list_top', slotname='blog_list_top', to='cms.Placeholder'),
        ),
    ]
