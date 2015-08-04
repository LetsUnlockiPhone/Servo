# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import servo.models.note


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0017_auto_20150430_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='escalation',
            field=servo.models.note.UnsavedForeignKey(editable=False, to='servo.Escalation', null=True),
        ),
    ]
