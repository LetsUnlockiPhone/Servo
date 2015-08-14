# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0023_auto_20150612_0822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gsxaccount',
            name='password',
        ),
        migrations.RemoveField(
            model_name='user',
            name='gsx_password',
        ),
    ]
