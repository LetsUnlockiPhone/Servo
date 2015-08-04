# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0002_auto_20141123_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='is_company',
            field=models.BooleanField(default=False, help_text='Companies can contain contacts', verbose_name='company'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='warranty_status',
            field=models.CharField(default=b'NA', max_length=3, verbose_name='Warranty Status', choices=[(b'QP', 'Quality Program'), (b'CS', 'Customer Satisfaction'), (b'ALW', 'Apple Limited Warranty'), (b'APP', 'AppleCare Protection Plan'), (b'CC', 'Custom Bid Contracts'), (b'CBC', 'Custom Bid Contracts'), (b'WTY', "3'rd Party Warranty"), (b'OOW', 'Out Of Warranty (No Coverage)'), (b'NA', 'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='closed_by',
            field=models.ForeignKey(related_name='closed_orders', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='component_code',
            field=models.CharField(default=b'', max_length=1, verbose_name='component group', blank=True, choices=[(b'0', b'General'), (b'1', b'Visual'), (b'2', b'Displays'), (b'3', b'Mass Storage'), (b'4', b'Input Devices'), (b'5', b'Boards'), (b'6', b'Power'), (b'7', b'Printer'), (b'8', b'Multi-function Device'), (b'9', b'Communication Devices'), (b'A', b'Share'), (b'B', b'iPhone'), (b'E', b'iPod'), (b'F', b'iPad'), (b'G', b'Beats Products')]),
            preserve_default=True,
        ),
    ]
