# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '__first__'),
        ('djangocms_blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='sites',
            field=models.ManyToManyField(help_text='Select sites in which to show the post. If none is set it will bevisible in all the configured sites.', to='sites.Site', null=True, verbose_name='Site(s', blank=True),
            preserve_default=True,
        ),
    ]
