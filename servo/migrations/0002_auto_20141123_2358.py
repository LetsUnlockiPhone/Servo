# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import servo.defaults


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='code',
            field=models.CharField(default=servo.defaults.uid, unique=True, max_length=36),
            preserve_default=True,
        ),
    ]
