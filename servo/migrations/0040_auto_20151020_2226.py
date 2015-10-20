# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0039_auto_20151016_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='repair',
            name='acplus',
            field=models.NullBooleanField(default=None, help_text='Unit is covered by AppleCare+'),
        ),
        migrations.AlterField(
            model_name='template',
            name='content',
            field=models.TextField(verbose_name='Content'),
        ),
        migrations.AlterField(
            model_name='template',
            name='title',
            field=models.CharField(default='New Template', unique=True, max_length=128, verbose_name='Title'),
        ),
    ]
