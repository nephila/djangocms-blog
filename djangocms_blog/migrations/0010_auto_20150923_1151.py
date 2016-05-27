 #-*- coding: utf-8 -*-
from __future__ import unicode_literals

import aldryn_apphooks_config.fields
import app_data.fields
import djangocms_text_ckeditor.fields
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '__first__'),
        ('djangocms_blog', '0009_latestpostsplugin_tags_new'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('type', models.CharField(verbose_name='type', max_length=100)),
                ('namespace', models.CharField(default=None, verbose_name='instance namespace', unique=True, max_length=100)),
                ('app_data', app_data.fields.AppDataField(editable=False, default='{}')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BlogConfigTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('language_code', models.CharField(db_index=True, verbose_name='Language', max_length=15)),
                ('app_title', models.CharField(verbose_name='application title', max_length=234)),
                ('master', models.ForeignKey(editable=False, to='djangocms_blog.BlogConfig', related_name='translations', null=True)),
            ],
            options={
                'verbose_name': 'blog config Translation',
                'db_table': 'djangocms_blog_blogconfig_translation',
                'default_permissions': (),
                'db_tablespace': '',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='GenericBlogPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, serialize=False, primary_key=True, auto_created=True, to='cms.CMSPlugin')),
                ('app_config', aldryn_apphooks_config.fields.AppHookConfigField(verbose_name='app. config', blank=True, to='djangocms_blog.BlogConfig', help_text='When selecting a value, the form is reloaded to get the updated default')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AlterField(
            model_name='posttranslation',
            name='abstract',
            field=djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='abstract', blank=True),
        ),
        migrations.AddField(
            model_name='authorentriesplugin',
            name='app_config',
            field=aldryn_apphooks_config.fields.AppHookConfigField(default=None, blank=True, verbose_name='app. config', to='djangocms_blog.BlogConfig', help_text='When selecting a value, the form is reloaded to get the updated default', null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='app_config',
            field=aldryn_apphooks_config.fields.AppHookConfigField(default=None, verbose_name='app. config', to='djangocms_blog.BlogConfig', help_text='When selecting a value, the form is reloaded to get the updated default', null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='latestpostsplugin',
            name='app_config',
            field=aldryn_apphooks_config.fields.AppHookConfigField(default=None, blank=True, verbose_name='app. config', to='djangocms_blog.BlogConfig', help_text='When selecting a value, the form is reloaded to get the updated default', null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='post',
            name='app_config',
            field=aldryn_apphooks_config.fields.AppHookConfigField(default=None, verbose_name='app. config', to='djangocms_blog.BlogConfig', help_text='When selecting a value, the form is reloaded to get the updated default', null=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='blogconfigtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterField(
            model_name='post',
            name='sites',
            field=models.ManyToManyField(to='sites.Site', help_text='Select sites in which to show the post. If none is set it will be visible in all the configured sites.', blank=True, verbose_name='Site(s)'),
        ),
    ]
