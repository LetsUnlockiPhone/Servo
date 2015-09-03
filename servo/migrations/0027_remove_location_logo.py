# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0026_auto_20150826_1323'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='logo',
        ),
    ]
