# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0003_auto_20141217_0029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessory',
            name='name',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
