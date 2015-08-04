# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.manager
import servo.models.account
import django.core.validators
import django.contrib.auth.models
import servo.defaults
import django.contrib.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0016_auto_20150316_1152'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='attachment',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='checklist',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='customer',
            managers=[
                (b'objects', django.db.models.manager.Manager()),
                (b'on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='device',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='event',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='flaggeditem',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='invoice',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='note',
            managers=[
                (b'objects', django.db.models.manager.Manager()),
                (b'on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='order',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='productcategory',
            managers=[
                (b'objects', django.db.models.manager.Manager()),
                (b'on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='queue',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='rateditem',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='tag',
            managers=[
                (b'objects', django.db.models.manager.Manager()),
                (b'on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='taggeditem',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='timeditem',
            managers=[
                (b'objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                (b'objects', django.contrib.auth.models.UserManager()),
                (b'techies', servo.models.account.TechieManager()),
                (b'active', servo.models.account.ActiveManager()),
            ],
        ),
        migrations.AlterField(
            model_name='checklist',
            name='queues',
            field=models.ManyToManyField(to='servo.Queue', verbose_name='queue', blank=True),
        ),
        migrations.AlterField(
            model_name='condition',
            name='key',
            field=models.CharField(max_length=16, choices=[(b'QUEUE', 'Queue'), (b'STATUS', 'Status'), (b'DEVICE', 'Device name'), (b'CUSTOMER_NAME', 'Customer name')]),
        ),
        migrations.AlterField(
            model_name='condition',
            name='operator',
            field=models.CharField(default=b'^%s$', max_length=4, choices=[(b'^%s$', 'Equals'), (b'%s', 'Contains'), (b'%d < %d', 'Less than'), (b'%d > %d', 'Greater than')]),
        ),
        migrations.AlterField(
            model_name='customer',
            name='devices',
            field=models.ManyToManyField(verbose_name='devices', editable=False, to='servo.Device', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(default=b'', max_length=254, verbose_name='email', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='groups',
            field=models.ManyToManyField(to='servo.CustomerGroup', verbose_name='Groups', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='tags',
            field=models.ManyToManyField(to='servo.Tag', verbose_name='tags', blank=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='products',
            field=models.ManyToManyField(help_text='Products that are compatible with this device instance', to='servo.Product', editable=False),
        ),
        migrations.AlterField(
            model_name='device',
            name='purchase_country',
            field=models.CharField(default=servo.defaults.country, editable=False, choices=[('AF', 'Afghanistan'), ('AX', '\xc5land Islands'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'), ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'), ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BT', 'Bhutan'), ('BO', 'Bolivia'), ('BQ', 'Bonaire, Sint Eustatius and Saba'), ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'), ('BV', 'Bouvet Island'), ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('BN', 'Brunei'), ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('CV', 'Cabo Verde'), ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('KY', 'Cayman Islands'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'), ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'), ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo (the Democratic Republic of the)'), ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('CI', "C\xf4te d'Ivoire"), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CW', 'Cura\xe7ao'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('ET', 'Ethiopia'), ('FK', 'Falkland Islands  [Malvinas]'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'), ('TF', 'French Southern Territories'), ('GA', 'Gabon'), ('GM', 'Gambia'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'), ('HM', 'Heard Island and McDonald Islands'), ('VA', 'Holy See'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran'), ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IM', 'Isle of Man'), ('IL', 'Israel'), ('IT', 'Italy'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', 'Laos'), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'), ('MK', 'Macedonia'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'), ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'), ('FM', 'Micronesia (Federated States of)'), ('MD', 'Moldovia'), ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('KP', 'North Korea'), ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestine, State of'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('RE', 'R\xe9union'), ('RO', 'Romania'), ('RU', 'Russia'), ('RW', 'Rwanda'), ('BL', 'Saint Barth\xe9lemy'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin (French part)'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'), ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'), ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SX', 'Sint Maarten (Dutch part)'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'), ('GS', 'South Georgia and the South Sandwich Islands'), ('KR', 'South Korea'), ('SS', 'South Sudan'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SJ', 'Svalbard and Jan Mayen'), ('SZ', 'Swaziland'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('SY', 'Syria'), ('TW', 'Taiwan'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania'), ('TH', 'Thailand'), ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'), ('GB', 'United Kingdom of Great Britain and Northern Ireland'), ('UM', 'United States Minor Outlying Islands'), ('US', 'United States of America'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VE', 'Venezuela'), ('VN', 'Vietnam'), ('VG', 'Virgin Islands (British)'), ('VI', 'Virgin Islands (U.S.)'), ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')], max_length=128, blank=True, verbose_name='Purchase Country'),
        ),
        migrations.AlterField(
            model_name='location',
            name='email',
            field=models.EmailField(default=b'', max_length=254, verbose_name='email', blank=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='gsx_accounts',
            field=models.ManyToManyField(to='servo.GsxAccount', verbose_name='Accounts', blank=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='labels',
            field=models.ManyToManyField(to='servo.Tag', blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='devices',
            field=models.ManyToManyField(to='servo.Device', through='servo.OrderDevice'),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.IntegerField(default=0, choices=[(0, 'Unassigned'), (1, 'Open'), (2, 'Closed')]),
        ),
        migrations.AlterField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(to='servo.ProductCategory', verbose_name='Categories', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='device_models',
            field=models.ManyToManyField(to='servo.DeviceGroup', verbose_name='device models', blank=True),
        ),
        migrations.AlterField(
            model_name='shippingmethod',
            name='notify_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='status',
            name='queue',
            field=models.ManyToManyField(to='servo.Queue', editable=False, through='servo.QueueStatus'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(null=True, verbose_name='last login', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='locations',
            field=models.ManyToManyField(to='servo.Location', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='queues',
            field=models.ManyToManyField(to='servo.Queue', verbose_name='queues', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username'),
        ),
    ]
