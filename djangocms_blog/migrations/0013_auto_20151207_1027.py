# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0012_auto_20151106_1519'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blogcategorytranslation',
            options={'verbose_name_plural': 'BlogCategory translations', 'verbose_name': 'BlogCategory translation'},
        ),
        migrations.AlterField(
            model_name='blogcategorytranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', choices=[('ar', 'Arabic'), ('en', 'English')], db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blogcategorytranslation',
            name='master',
            field=models.ForeignKey(to='djangocms_blog.BlogCategory', null=True, related_name='translations'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blogcategorytranslation',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blogcategorytranslation',
            name='slug',
            field=models.SlugField(verbose_name='Slug', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', choices=[('ar', 'Arabic'), ('en', 'English')], db_index=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='blogcategorytranslation',
            unique_together=set([('master', 'language_code')]),
        ),
        migrations.AlterModelTable(
            name='blogcategorytranslation',
            table=None,
        ),
    ]
