# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0035_auto_20150930_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderitem',
            name='purchase_order_ref',
            field=models.CharField(default=b'', max_length=32, editable=False),
        ),
    ]
