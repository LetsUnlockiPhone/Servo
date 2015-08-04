# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0018_auto_20150505_0020'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-priority', 'id'), 'permissions': (('change_user', 'Can set assignee'), ('change_status', 'Can change status'), ('follow_order', 'Can follow order'), ('copy_order', 'Can copy order'), ('batch_process', 'Can batch process'))},
        ),
    ]
