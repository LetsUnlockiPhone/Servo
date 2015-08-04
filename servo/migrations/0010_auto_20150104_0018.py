# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import servo.defaults


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0009_auto_20150101_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='subject',
            field=models.CharField(default=servo.defaults.subject, max_length=255, verbose_name='Subject', blank=True),
            preserve_default=True,
        ),
    ]
