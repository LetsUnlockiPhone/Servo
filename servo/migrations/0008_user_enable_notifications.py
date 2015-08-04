# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0007_auto_20150101_2318'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='enable_notifications',
            field=models.BooleanField(default=True, help_text='Enable notifications in the toolbar.', verbose_name='Enable notifications'),
            preserve_default=True,
        ),
    ]
