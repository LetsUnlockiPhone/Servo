# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0004_auto_20141229_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(related_name='orders', on_delete=django.db.models.deletion.SET_NULL, to='servo.Customer', null=True),
            preserve_default=True,
        ),
    ]
