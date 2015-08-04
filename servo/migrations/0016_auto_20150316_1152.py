# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0015_auto_20150208_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(default=b'SEND_EMAIL', max_length=32, choices=[(b'SEND_SMS', 'Send SMS'), (b'SEND_EMAIL', 'Send email'), (b'ADD_TAG', 'Add Tag'), (b'SET_PRIO', 'Set Priority'), (b'SET_QUEUE', 'Set Queue'), (b'SET_USER', 'Assign to')])),
                ('value', models.TextField(default=b'')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=16, choices=[(b'QUEUE', 'Queue'), (b'STATUS', 'Status'), (b'CUSTOMER_NAME', 'Customer name'), (b'DEVICE', 'Device name')])),
                ('operator', models.CharField(max_length=4, choices=[(b'^%s$', 'Equals'), (b'%s', 'Contains'), (b'%d < %d', 'Less than'), (b'%d > %d', 'Greater than')])),
                ('value', models.TextField(default=b'')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(default='New Rule', max_length=128)),
                ('match', models.CharField(default=b'ANY', max_length=3, choices=[(b'ANY', 'Any'), (b'ALL', 'All')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='condition',
            name='rule',
            field=models.ForeignKey(to='servo.Rule'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='action',
            name='rule',
            field=models.ForeignKey(to='servo.Rule'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='customer',
            field=mptt.fields.TreeForeignKey(blank=True, to='servo.Customer', null=True),
            preserve_default=True,
        ),
    ]
