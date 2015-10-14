# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0037_purchaseorderitem_user_fullname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='carrier',
            field=models.CharField(default=b'', max_length=18, verbose_name='Carrier', blank=True, choices=[(b'XAER', b'Aero 2000'), (b'XAIRBEC', b'Airborne'), (b'XAIRB', b'Airborne'), (b'XARM', b'Aramex'), (b'XOZP', b'Australia Post'), (b'XBAX', b'BAX GLOBAL PTE LTD'), (b'XCPW', b'CPW Internal'), (b'XCL', b'Citylink'), (b'XDHL', b'DHL'), (b'XDHLC', b'DHL'), (b'XDZNA', b'Danzas-AEI'), (b'XEAS', b'EAS'), (b'XEGL', b'Eagle ASIA PACIFIC HOLDINGS'), (b'XEXXN', b'Exel'), (b'XFEDE', b'FedEx'), (b'XFDE', b'FedEx Air'), (b'XGLS', b'GLS-General Logistics Systems'), (b'XHNF', b'H and Friends'), (b'XNGLN', b'Nightline'), (b'XPL', b'Parceline'), (b'XPRLA', b'Purolator'), (b'SDS', b'SDS An Post'), (b'XSNO', b'Seino Transportation Co. Ltd.'), (b'XSTE', b'Star Track Express'), (b'XTNT', b'TNT'), (b'XUPSN', b'UPS'), (b'XUTI', b'UTi (Japan) K.K.'), (b'XYMT', b'YAMATO')]),
        ),
    ]
