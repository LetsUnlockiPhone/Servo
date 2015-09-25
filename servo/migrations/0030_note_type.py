# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0029_auto_20150921_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='type',
            field=models.IntegerField(default=0, verbose_name='Type', choices=[(0, 'Note'), (1, 'Problem'), (2, 'Escalation')]),
        ),
    ]
