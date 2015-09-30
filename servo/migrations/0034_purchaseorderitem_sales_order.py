# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0033_auto_20150930_0937'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderitem',
            name='sales_order',
            field=models.ForeignKey(editable=False, to='servo.Order', null=True, verbose_name='Sales Order'),
        ),
    ]
