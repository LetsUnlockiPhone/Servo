# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import servo.lib.shorturl


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0032_auto_20150929_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='code',
            field=models.CharField(default=servo.lib.shorturl.from_time, unique=True, max_length=32, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='product',
            name='component_code',
            field=models.CharField(default=b'', max_length=1, verbose_name='Component group', blank=True, choices=[(b'0', b'General'), (b'1', b'Visual'), (b'2', b'Displays'), (b'3', b'Mass Storage'), (b'4', b'Input Devices'), (b'5', b'Boards'), (b'6', b'Power'), (b'7', b'Printer'), (b'8', b'Multi-function Device'), (b'9', b'Communication Devices'), (b'A', b'Share'), (b'B', b'iPhone'), (b'E', b'iPod'), (b'F', b'iPad'), (b'G', b'Beats Products'), (b'W', b'Apple Watch')]),
        ),
        migrations.AlterField(
            model_name='product',
            name='device_models',
            field=models.ManyToManyField(to='servo.DeviceGroup', verbose_name='Device models', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='is_serialized',
            field=models.BooleanField(default=False, help_text='Product has a serial number', verbose_name='Is serialized'),
        ),
        migrations.AlterField(
            model_name='product',
            name='part_type',
            field=models.CharField(default=b'OTHER', max_length=18, verbose_name='Part type', choices=[(b'ADJUSTMENT', 'Adjustment'), (b'MODULE', 'Module'), (b'REPLACEMENT', 'Replacement'), (b'SERVICE', 'Service'), (b'SERVICE CONTRACT', 'Service Contract'), (b'OTHER', 'Other')]),
        ),
        migrations.AlterField(
            model_name='product',
            name='photo',
            field=models.ImageField(upload_to=b'products', null=True, verbose_name='Photo', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='shipping',
            field=models.FloatField(default=0, verbose_name='Shipping'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='carrier',
            field=models.CharField(max_length=32, verbose_name='Carrier', blank=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='confirmation',
            field=models.CharField(default=b'', max_length=32, verbose_name='Confirmation', blank=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='days_delivered',
            field=models.IntegerField(default=1, verbose_name='Delivery Time', blank=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='reference',
            field=models.CharField(default=b'', max_length=32, verbose_name='Reference', blank=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='supplier',
            field=models.CharField(max_length=32, verbose_name='Supplier', blank=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='tracking_id',
            field=models.CharField(max_length=128, verbose_name='Tracking ID', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='locale',
            field=models.CharField(default=b'da_DK.UTF-8', help_text='Select which language you want to use Servo in.', max_length=32, verbose_name='Language', choices=[(b'da_DK.UTF-8', 'Danish'), (b'nl_NL.UTF-8', 'Dutch'), (b'en_US.UTF-8', 'English'), (b'et_EE.UTF-8', 'Estonian'), (b'fi_FI.UTF-8', 'Finnish'), (b'sv_SE.UTF-8', 'Swedish')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='notify_by_email',
            field=models.BooleanField(default=False, help_text='Event notifications will also be emailed to you.', verbose_name='Email notifications'),
        ),
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(help_text='Maximum avatar size is 1MB', upload_to=b'avatars', null=True, verbose_name='Photo', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='tech_id',
            field=models.CharField(default=b'', max_length=16, verbose_name='Tech ID', blank=True),
        ),
    ]
