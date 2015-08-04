# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0010_auto_20150104_0018'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='next_tether_policy',
            field=models.CharField(default=b'', verbose_name='Next Tether Policy', max_length=128, editable=False),
            preserve_default=True,
        ),
    ]
