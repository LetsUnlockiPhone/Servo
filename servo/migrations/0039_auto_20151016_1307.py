# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0038_auto_20151013_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='configuration',
            field=models.CharField(default=b'', max_length=256, verbose_name='Configuration', blank=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='description',
            field=models.CharField(default='New Device', max_length=128, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='device',
            name='is_vintage',
            field=models.BooleanField(default=False, help_text='Device is considered vintage in GSX', verbose_name='Vintage'),
        ),
        migrations.AlterField(
            model_name='device',
            name='password',
            field=models.CharField(default=b'', max_length=32, verbose_name='Password', blank=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='photo',
            field=models.ImageField(upload_to=b'devices', null=True, verbose_name='Photo', blank=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='username',
            field=models.CharField(default=b'', max_length=32, verbose_name='Username', blank=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(default=b'', max_length=32, verbose_name='Address', blank=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='city',
            field=models.CharField(default=b'', max_length=16, verbose_name='City', blank=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='email',
            field=models.EmailField(default=b'', max_length=254, verbose_name='Email', blank=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='phone',
            field=models.CharField(default=b'', max_length=32, verbose_name='Phone', blank=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='title',
            field=models.CharField(default='New Location', max_length=255, verbose_name='Name'),
        ),
    ]
