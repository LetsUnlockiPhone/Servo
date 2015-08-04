# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0013_auto_20150204_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderstatus',
            name='duration',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
