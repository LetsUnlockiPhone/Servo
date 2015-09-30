# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0034_purchaseorderitem_sales_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderitem',
            name='sales_order_ref',
            field=models.CharField(default=b'', max_length=8, editable=False),
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='sales_order',
            field=models.ForeignKey(editable=False, to='servo.Order', null=True),
        ),
    ]
