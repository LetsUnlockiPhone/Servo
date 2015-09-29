# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0031_auto_20150929_0010'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='location',
            field=models.ForeignKey(blank=True, editable=False, to='servo.Location', null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name='Paid'),
        ),
    ]
