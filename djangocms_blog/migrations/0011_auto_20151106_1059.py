# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0010_auto_20151105_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogcategory',
            name='sites',
            field=models.ManyToManyField(to='sites.Site', help_text='Select sites in which to show the categpry. If no site is set it will choose the current site.', blank=True, null=True, verbose_name='Site(s)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blogcategorytranslation',
            name='language_code',
            field=models.CharField(max_length=15, choices=[('en', 'English')], db_index=True, verbose_name='Language'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='post',
            name='sites',
            field=models.ManyToManyField(to='sites.Site', help_text='Select sites in which to show the post. If no site is set it will choose the current site.', blank=True, null=True, verbose_name='Site(s)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='language_code',
            field=models.CharField(max_length=15, choices=[('en', 'English')], db_index=True, verbose_name='Language'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='blogcategorytranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='posttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
