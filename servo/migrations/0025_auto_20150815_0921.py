# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0024_auto_20150813_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='repair',
            name='issue_code',
            field=models.CharField(default=b'', max_length=7),
        ),
        migrations.AddField(
            model_name='repair',
            name='symptom_code',
            field=models.CharField(default=b'', max_length=7),
        ),
        migrations.AlterField(
            model_name='device',
            name='product_line',
            field=models.CharField(default=b'OTHER', max_length=16, verbose_name='Product Line', choices=[(b'IPODCLASSIC', b'iPod Classic'), (b'POWERMAC', b'Power Mac'), (b'APPLETV', b'Apple TV'), (b'IMAC', b'iMac'), (b'OTHER', b'Other Products'), (b'MACBOOKAIR', b'MacBook Air'), (b'DISPLAYS', b'Display'), (b'IPODTOUCH', b'iPod Touch'), (b'MACPRO', b'Mac Pro'), (b'IPODNANO', b'iPod nano'), (b'IPAD', b'iPad'), (b'MACBOOK', b'MacBook'), (b'MACACCESSORY', b'Mac Accessory'), (b'MACMINI', b'Mac mini'), (b'BEATS', b'Beats Products'), (b'SERVER', b'Server'), (b'MACBOOKLEGACY', b'MacBook'), (b'IPHONE', b'iPhone'), (b'IPHONEACCESSORY', b'iPhone Accessory'), (b'IPODSHUFFLE', b'iPod Shuffle'), (b'MACBOOKPRO', b'MacBook Pro')]),
        ),
        migrations.AlterField(
            model_name='product',
            name='component_code',
            field=models.CharField(default=b'', max_length=1, verbose_name='component group', blank=True, choices=[(b'0', b'General'), (b'1', b'Visual'), (b'2', b'Displays'), (b'3', b'Mass Storage'), (b'4', b'Input Devices'), (b'5', b'Boards'), (b'6', b'Power'), (b'7', b'Printer'), (b'8', b'Multi-function Device'), (b'9', b'Communication Devices'), (b'A', b'Share'), (b'B', b'iPhone'), (b'E', b'iPod'), (b'F', b'iPad'), (b'G', b'Beats Products'), (b'W', b'Apple Watch')]),
        ),
    ]
