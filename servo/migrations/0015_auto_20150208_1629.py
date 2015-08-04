# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0014_orderstatus_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderstatus',
            name='started_at',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
