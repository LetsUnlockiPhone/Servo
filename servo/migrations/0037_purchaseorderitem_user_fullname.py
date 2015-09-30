# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0036_purchaseorderitem_purchase_order_ref'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderitem',
            name='user_fullname',
            field=models.CharField(default=b'', max_length=256, editable=False),
        ),
    ]
