# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_blog', '0011_auto_20151106_1059'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blogcategorytranslation',
            options={'verbose_name': 'Category Translation', 'managed': True, 'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='posttranslation',
            options={'verbose_name': 'News Translation', 'managed': True, 'default_permissions': ()},
        ),
        migrations.AlterUniqueTogether(
            name='blogcategorytranslation',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='posttranslation',
            unique_together=set([]),
        ),
    ]
