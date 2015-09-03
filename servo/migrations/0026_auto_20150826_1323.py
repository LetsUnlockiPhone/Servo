# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0025_auto_20150815_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcategory',
            name='title',
            field=models.CharField(default='New Category', unique=True, max_length=255),
        ),
    ]
