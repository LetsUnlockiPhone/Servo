# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0043_auto_20151109_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendar',
            name='hours_per_day',
            field=models.FloatField(help_text='How many hours per day should be in this calendar', null=True, verbose_name='Hours per day', blank=True),
        ),
    ]
