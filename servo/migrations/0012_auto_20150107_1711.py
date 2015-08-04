# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0011_device_next_tether_policy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='product_line',
            field=models.CharField(default=b'OTHER', max_length=16, verbose_name='Product Line', choices=[(b'IPODCLASSIC', b'iPod Classic'), (b'POWERMAC', b'Power Mac'), (b'APPLETV', b'Apple TV'), (b'IMAC', b'iMac'), (b'OTHER', b'Other Products'), (b'MACBOOKAIR', b'MacBook Air'), (b'DISPLAYS', b'Display'), (b'IPODTOUCH', b'iPod Touch'), (b'MACPRO', b'Mac Pro'), (b'IPODNANO', b'iPod nano'), (b'IPAD', b'iPad'), (b'MACBOOK', b'MacBook'), (b'MACACCESSORY', b'Mac Accessory'), (b'MACMINI', b'Mac mini'), (b'SERVER', b'Server'), (b'BEATS', b'Beats Products'), (b'IPHONE', b'iPhone'), (b'IPHONEACCESSORY', b'iPhone Accessory'), (b'IPODSHUFFLE', b'iPod Shuffle'), (b'MACBOOKPRO', b'MacBook Pro')]),
            preserve_default=True,
        ),
    ]
