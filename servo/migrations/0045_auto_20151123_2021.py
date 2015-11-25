# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0044_auto_20151118_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='checkin',
            field=models.BooleanField(default=True, verbose_name='Use for check-in'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='amount_minimum',
            field=models.PositiveIntegerField(default=0, verbose_name='Minimum amount'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='amount_ordered',
            field=models.PositiveIntegerField(default=0, verbose_name='Ordered amount'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='amount_reserved',
            field=models.PositiveIntegerField(default=0, verbose_name='Reserved amount'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='amount_stocked',
            field=models.IntegerField(default=0, verbose_name='Stocked amount'),
        ),
    ]
