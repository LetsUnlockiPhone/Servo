# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0040_auto_20151020_2226'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuestatus',
            name='idx',
            field=models.IntegerField(default=1, verbose_name='Ordering'),
        ),
        migrations.AlterField(
            model_name='repair',
            name='acplus',
            field=models.NullBooleanField(default=None, help_text='Repair is covered by AppleCare+', verbose_name='AppleCare+'),
        ),
        migrations.AlterField(
            model_name='repair',
            name='consumer_law',
            field=models.NullBooleanField(default=None, help_text='Repair is eligible for consumer law coverage'),
        ),
    ]
