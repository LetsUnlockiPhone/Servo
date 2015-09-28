# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import servo.defaults


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0030_note_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='country',
            field=models.CharField(default=servo.defaults.country, max_length=2, verbose_name='Country', blank=True, choices=[('AD', 'Andorra'), ('AE', 'United Arab Emirates'), ('AF', 'Afghanistan'), ('AG', 'Antigua & Barbuda'), ('AI', 'Anguilla'), ('AL', 'Albania'), ('AM', 'Armenia'), ('AO', 'Angola'), ('AQ', 'Antarctica'), ('AR', 'Argentina'), ('AS', 'Samoa (American)'), ('AT', 'Austria'), ('AU', 'Australia'), ('AW', 'Aruba'), ('AX', '\xc5land Islands'), ('AZ', 'Azerbaijan'), ('BA', 'Bosnia & Herzegovina'), ('BB', 'Barbados'), ('BD', 'Bangladesh'), ('BE', 'Belgium'), ('BF', 'Burkina Faso'), ('BG', 'Bulgaria'), ('BH', 'Bahrain'), ('BI', 'Burundi'), ('BJ', 'Benin'), ('BL', 'St Barthelemy'), ('BM', 'Bermuda'), ('BN', 'Brunei'), ('BO', 'Bolivia'), ('BQ', 'Caribbean Netherlands'), ('BR', 'Brazil'), ('BS', 'Bahamas'), ('BT', 'Bhutan'), ('BV', 'Bouvet Island'), ('BW', 'Botswana'), ('BY', 'Belarus'), ('BZ', 'Belize'), ('CA', 'Canada'), ('CC', 'Cocos (Keeling) Islands'), ('CD', 'Congo (Dem. Rep.)'), ('CF', 'Central African Rep.'), ('CG', 'Congo (Rep.)'), ('CH', 'Switzerland'), ('CI', "C\xf4te d'Ivoire"), ('CK', 'Cook Islands'), ('CL', 'Chile'), ('CM', 'Cameroon'), ('CN', 'China'), ('CO', 'Colombia'), ('CR', 'Costa Rica'), ('CU', 'Cuba'), ('CV', 'Cape Verde'), ('CW', 'Curacao'), ('CX', 'Christmas Island'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DE', 'Germany'), ('DJ', 'Djibouti'), ('DK', 'Denmark'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('DZ', 'Algeria'), ('EC', 'Ecuador'), ('EE', 'Estonia'), ('EG', 'Egypt'), ('EH', 'Western Sahara'), ('ER', 'Eritrea'), ('ES', 'Spain'), ('ET', 'Ethiopia'), ('FI', 'Finland'), ('FJ', 'Fiji'), ('FK', 'Falkland Islands'), ('FM', 'Micronesia'), ('FO', 'Faroe Islands'), ('FR', 'France'), ('GA', 'Gabon'), ('GB', 'Britain (UK)'), ('GD', 'Grenada'), ('GE', 'Georgia'), ('GF', 'French Guiana'), ('GG', 'Guernsey'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GL', 'Greenland'), ('GM', 'Gambia'), ('GN', 'Guinea'), ('GP', 'Guadeloupe'), ('GQ', 'Equatorial Guinea'), ('GR', 'Greece'), ('GS', 'South Georgia & the South Sandwich Islands'), ('GT', 'Guatemala'), ('GU', 'Guam'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HK', 'Hong Kong'), ('HM', 'Heard Island & McDonald Islands'), ('HN', 'Honduras'), ('HR', 'Croatia'), ('HT', 'Haiti'), ('HU', 'Hungary'), ('ID', 'Indonesia'), ('IE', 'Ireland'), ('IL', 'Israel'), ('IM', 'Isle of Man'), ('IN', 'India'), ('IO', 'British Indian Ocean Territory'), ('IQ', 'Iraq'), ('IR', 'Iran'), ('IS', 'Iceland'), ('IT', 'Italy'), ('JE', 'Jersey'), ('JM', 'Jamaica'), ('JO', 'Jordan'), ('JP', 'Japan'), ('KE', 'Kenya'), ('KG', 'Kyrgyzstan'), ('KH', 'Cambodia'), ('KI', 'Kiribati'), ('KM', 'Comoros'), ('KN', 'St Kitts & Nevis'), ('KP', 'Korea (North)'), ('KR', 'Korea (South)'), ('KW', 'Kuwait'), ('KY', 'Cayman Islands'), ('KZ', 'Kazakhstan'), ('LA', 'Laos'), ('LB', 'Lebanon'), ('LC', 'St Lucia'), ('LI', 'Liechtenstein'), ('LK', 'Sri Lanka'), ('LR', 'Liberia'), ('LS', 'Lesotho'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('LV', 'Latvia'), ('LY', 'Libya'), ('MA', 'Morocco'), ('MC', 'Monaco'), ('MD', 'Moldova'), ('ME', 'Montenegro'), ('MF', 'St Martin (French part)'), ('MG', 'Madagascar'), ('MH', 'Marshall Islands'), ('MK', 'Macedonia'), ('ML', 'Mali'), ('MM', 'Myanmar (Burma)'), ('MN', 'Mongolia'), ('MO', 'Macau'), ('MP', 'Northern Mariana Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MS', 'Montserrat'), ('MT', 'Malta'), ('MU', 'Mauritius'), ('MV', 'Maldives'), ('MW', 'Malawi'), ('MX', 'Mexico'), ('MY', 'Malaysia'), ('MZ', 'Mozambique'), ('NA', 'Namibia'), ('NC', 'New Caledonia'), ('NE', 'Niger'), ('NF', 'Norfolk Island'), ('NG', 'Nigeria'), ('NI', 'Nicaragua'), ('NL', 'Netherlands'), ('NO', 'Norway'), ('NP', 'Nepal'), ('NR', 'Nauru'), ('NU', 'Niue'), ('NZ', 'New Zealand'), ('OM', 'Oman'), ('PA', 'Panama'), ('PE', 'Peru'), ('PF', 'French Polynesia'), ('PG', 'Papua New Guinea'), ('PH', 'Philippines'), ('PK', 'Pakistan'), ('PL', 'Poland'), ('PM', 'St Pierre & Miquelon'), ('PN', 'Pitcairn'), ('PR', 'Puerto Rico'), ('PS', 'Palestine'), ('PT', 'Portugal'), ('PW', 'Palau'), ('PY', 'Paraguay'), ('QA', 'Qatar'), ('RE', 'R\xe9union'), ('RO', 'Romania'), ('RS', 'Serbia'), ('RU', 'Russia'), ('RW', 'Rwanda'), ('SA', 'Saudi Arabia'), ('SB', 'Solomon Islands'), ('SC', 'Seychelles'), ('SD', 'Sudan'), ('SE', 'Sweden'), ('SG', 'Singapore'), ('SH', 'St Helena'), ('SI', 'Slovenia'), ('SJ', 'Svalbard & Jan Mayen'), ('SK', 'Slovakia'), ('SL', 'Sierra Leone'), ('SM', 'San Marino'), ('SN', 'Senegal'), ('SO', 'Somalia'), ('SR', 'Suriname'), ('SS', 'South Sudan'), ('ST', 'Sao Tome & Principe'), ('SV', 'El Salvador'), ('SX', 'St Maarten (Dutch part)'), ('SY', 'Syria'), ('SZ', 'Swaziland'), ('TC', 'Turks & Caicos Is'), ('TD', 'Chad'), ('TF', 'French Southern & Antarctic Lands'), ('TG', 'Togo'), ('TH', 'Thailand'), ('TJ', 'Tajikistan'), ('TK', 'Tokelau'), ('TL', 'East Timor'), ('TM', 'Turkmenistan'), ('TN', 'Tunisia'), ('TO', 'Tonga'), ('TR', 'Turkey'), ('TT', 'Trinidad & Tobago'), ('TV', 'Tuvalu'), ('TW', 'Taiwan'), ('TZ', 'Tanzania'), ('UA', 'Ukraine'), ('UG', 'Uganda'), ('UM', 'US minor outlying islands'), ('US', 'United States'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VA', 'Vatican City'), ('VC', 'St Vincent'), ('VE', 'Venezuela'), ('VG', 'Virgin Islands (UK)'), ('VI', 'Virgin Islands (US)'), ('VN', 'Vietnam'), ('VU', 'Vanuatu'), ('WF', 'Wallis & Futuna'), ('WS', 'Samoa (western)'), ('YE', 'Yemen'), ('YT', 'Mayotte'), ('ZA', 'South Africa'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')]),
        ),
        migrations.AlterField(
            model_name='device',
            name='product_line',
            field=models.CharField(default=b'OTHER', max_length=16, verbose_name='Product Line', choices=[(b'IPODCLASSIC', b'iPod Classic'), (b'POWERMAC', b'Power Mac'), (b'APPLETV', b'Apple TV'), (b'IMAC', b'iMac'), (b'OTHER', b'Other Products'), (b'MACBOOKAIR', b'MacBook Air'), (b'DISPLAYS', b'Display'), (b'IPODTOUCH', b'iPod Touch'), (b'MACPRO', b'Mac Pro'), (b'IPODNANO', b'iPod nano'), (b'IPAD', b'iPad'), (b'MACBOOK', b'MacBook'), (b'MACACCESSORY', b'Mac Accessory'), (b'MACMINI', b'Mac mini'), (b'WATCH', b'Apple Watch'), (b'MACBOOKLEGACY', b'MacBook'), (b'SERVERS', b'Server'), (b'BEATS', b'Beats Products'), (b'IPHONE', b'iPhone'), (b'IPHONEACCESSORY', b'iPhone Accessory'), (b'IPODSHUFFLE', b'iPod Shuffle'), (b'MACBOOKPRO', b'MacBook Pro')]),
        ),
        migrations.AlterField(
            model_name='note',
            name='is_flagged',
            field=models.BooleanField(default=False, verbose_name='Flagged', editable=False),
        ),
        migrations.AlterField(
            model_name='note',
            name='is_read',
            field=models.BooleanField(default=True, verbose_name='Read', editable=False),
        ),
        migrations.AlterField(
            model_name='note',
            name='is_reported',
            field=models.BooleanField(default=False, verbose_name='Report'),
        ),
        migrations.AlterField(
            model_name='note',
            name='type',
            field=models.IntegerField(default=0, blank=True, verbose_name='Type', choices=[(0, 'Note'), (1, 'Problem'), (2, 'Escalation')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.IntegerField(default=0, choices=[(0, 'Unassigned'), (1, 'Open'), (2, 'Closed'), (3, 'Waiting')]),
        ),
    ]
