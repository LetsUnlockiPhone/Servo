# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0042_auto_20151026_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='title',
            field=models.CharField(default='New Location', unique=True, max_length=255, verbose_name='Name'),
        ),
    ]
