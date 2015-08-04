# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0020_auto_20150514_0618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='password',
            field=models.CharField(default=b'', max_length=32, verbose_name='password'),
        ),
        migrations.AlterField(
            model_name='device',
            name='purchased_on',
            field=models.DateField(null=True, verbose_name='Date of Purchase', blank=True),
        ),
    ]
