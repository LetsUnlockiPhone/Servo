# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import servo.validators
import servo.defaults


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0006_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklistitem',
            name='description',
            field=models.TextField(default=b'', verbose_name='Description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='customer',
            name='country',
            field=models.CharField(default=servo.defaults.country, max_length=2, verbose_name='Country', blank=True, choices=[('AD', 'Andorra'), ('AE', 'United Arab Emirates'), ('AF', 'Afghanistan'), ('AG', 'Antigua & Barbuda'), ('AI', 'Anguilla'), ('AL', 'Albania'), ('AM', 'Armenia'), ('AO', 'Angola'), ('AQ', 'Antarctica'), ('AR', 'Argentina'), ('AS', 'Samoa (American)'), ('AT', 'Austria'), ('AU', 'Australia'), ('AW', 'Aruba'), ('AX', 'Aaland Islands'), ('AZ', 'Azerbaijan'), ('BA', 'Bosnia & Herzegovina'), ('BB', 'Barbados'), ('BD', 'Bangladesh'), ('BE', 'Belgium'), ('BF', 'Burkina Faso'), ('BG', 'Bulgaria'), ('BH', 'Bahrain'), ('BI', 'Burundi'), ('BJ', 'Benin'), ('BL', 'St Barthelemy'), ('BM', 'Bermuda'), ('BN', 'Brunei'), ('BO', 'Bolivia'), ('BQ', 'Caribbean Netherlands'), ('BR', 'Brazil'), ('BS', 'Bahamas'), ('BT', 'Bhutan'), ('BV', 'Bouvet Island'), ('BW', 'Botswana'), ('BY', 'Belarus'), ('BZ', 'Belize'), ('CA', 'Canada'), ('CC', 'Cocos (Keeling) Islands'), ('CD', 'Congo (Dem. Rep.)'), ('CF', 'Central African Rep.'), ('CG', 'Congo (Rep.)'), ('CH', 'Switzerland'), ('CI', "Cote d'Ivoire"), ('CK', 'Cook Islands'), ('CL', 'Chile'), ('CM', 'Cameroon'), ('CN', 'China'), ('CO', 'Colombia'), ('CR', 'Costa Rica'), ('CU', 'Cuba'), ('CV', 'Cape Verde'), ('CW', 'Curacao'), ('CX', 'Christmas Island'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DE', 'Germany'), ('DJ', 'Djibouti'), ('DK', 'Denmark'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('DZ', 'Algeria'), ('EC', 'Ecuador'), ('EE', 'Estonia'), ('EG', 'Egypt'), ('EH', 'Western Sahara'), ('ER', 'Eritrea'), ('ES', 'Spain'), ('ET', 'Ethiopia'), ('FI', 'Finland'), ('FJ', 'Fiji'), ('FK', 'Falkland Islands'), ('FM', 'Micronesia'), ('FO', 'Faroe Islands'), ('FR', 'France'), ('GA', 'Gabon'), ('GB', 'Britain (UK)'), ('GD', 'Grenada'), ('GE', 'Georgia'), ('GF', 'French Guiana'), ('GG', 'Guernsey'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GL', 'Greenland'), ('GM', 'Gambia'), ('GN', 'Guinea'), ('GP', 'Guadeloupe'), ('GQ', 'Equatorial Guinea'), ('GR', 'Greece'), ('GS', 'South Georgia & the South Sandwich Islands'), ('GT', 'Guatemala'), ('GU', 'Guam'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HK', 'Hong Kong'), ('HM', 'Heard Island & McDonald Islands'), ('HN', 'Honduras'), ('HR', 'Croatia'), ('HT', 'Haiti'), ('HU', 'Hungary'), ('ID', 'Indonesia'), ('IE', 'Ireland'), ('IL', 'Israel'), ('IM', 'Isle of Man'), ('IN', 'India'), ('IO', 'British Indian Ocean Territory'), ('IQ', 'Iraq'), ('IR', 'Iran'), ('IS', 'Iceland'), ('IT', 'Italy'), ('JE', 'Jersey'), ('JM', 'Jamaica'), ('JO', 'Jordan'), ('JP', 'Japan'), ('KE', 'Kenya'), ('KG', 'Kyrgyzstan'), ('KH', 'Cambodia'), ('KI', 'Kiribati'), ('KM', 'Comoros'), ('KN', 'St Kitts & Nevis'), ('KP', 'Korea (North)'), ('KR', 'Korea (South)'), ('KW', 'Kuwait'), ('KY', 'Cayman Islands'), ('KZ', 'Kazakhstan'), ('LA', 'Laos'), ('LB', 'Lebanon'), ('LC', 'St Lucia'), ('LI', 'Liechtenstein'), ('LK', 'Sri Lanka'), ('LR', 'Liberia'), ('LS', 'Lesotho'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('LV', 'Latvia'), ('LY', 'Libya'), ('MA', 'Morocco'), ('MC', 'Monaco'), ('MD', 'Moldova'), ('ME', 'Montenegro'), ('MF', 'St Martin (French part)'), ('MG', 'Madagascar'), ('MH', 'Marshall Islands'), ('MK', 'Macedonia'), ('ML', 'Mali'), ('MM', 'Myanmar (Burma)'), ('MN', 'Mongolia'), ('MO', 'Macau'), ('MP', 'Northern Mariana Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MS', 'Montserrat'), ('MT', 'Malta'), ('MU', 'Mauritius'), ('MV', 'Maldives'), ('MW', 'Malawi'), ('MX', 'Mexico'), ('MY', 'Malaysia'), ('MZ', 'Mozambique'), ('NA', 'Namibia'), ('NC', 'New Caledonia'), ('NE', 'Niger'), ('NF', 'Norfolk Island'), ('NG', 'Nigeria'), ('NI', 'Nicaragua'), ('NL', 'Netherlands'), ('NO', 'Norway'), ('NP', 'Nepal'), ('NR', 'Nauru'), ('NU', 'Niue'), ('NZ', 'New Zealand'), ('OM', 'Oman'), ('PA', 'Panama'), ('PE', 'Peru'), ('PF', 'French Polynesia'), ('PG', 'Papua New Guinea'), ('PH', 'Philippines'), ('PK', 'Pakistan'), ('PL', 'Poland'), ('PM', 'St Pierre & Miquelon'), ('PN', 'Pitcairn'), ('PR', 'Puerto Rico'), ('PS', 'Palestine'), ('PT', 'Portugal'), ('PW', 'Palau'), ('PY', 'Paraguay'), ('QA', 'Qatar'), ('RE', 'Reunion'), ('RO', 'Romania'), ('RS', 'Serbia'), ('RU', 'Russia'), ('RW', 'Rwanda'), ('SA', 'Saudi Arabia'), ('SB', 'Solomon Islands'), ('SC', 'Seychelles'), ('SD', 'Sudan'), ('SE', 'Sweden'), ('SG', 'Singapore'), ('SH', 'St Helena'), ('SI', 'Slovenia'), ('SJ', 'Svalbard & Jan Mayen'), ('SK', 'Slovakia'), ('SL', 'Sierra Leone'), ('SM', 'San Marino'), ('SN', 'Senegal'), ('SO', 'Somalia'), ('SR', 'Suriname'), ('SS', 'South Sudan'), ('ST', 'Sao Tome & Principe'), ('SV', 'El Salvador'), ('SX', 'St Maarten (Dutch part)'), ('SY', 'Syria'), ('SZ', 'Swaziland'), ('TC', 'Turks & Caicos Is'), ('TD', 'Chad'), ('TF', 'French Southern & Antarctic Lands'), ('TG', 'Togo'), ('TH', 'Thailand'), ('TJ', 'Tajikistan'), ('TK', 'Tokelau'), ('TL', 'East Timor'), ('TM', 'Turkmenistan'), ('TN', 'Tunisia'), ('TO', 'Tonga'), ('TR', 'Turkey'), ('TT', 'Trinidad & Tobago'), ('TV', 'Tuvalu'), ('TW', 'Taiwan'), ('TZ', 'Tanzania'), ('UA', 'Ukraine'), ('UG', 'Uganda'), ('UM', 'US minor outlying islands'), ('US', 'United States'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VA', 'Vatican City'), ('VC', 'St Vincent'), ('VE', 'Venezuela'), ('VG', 'Virgin Islands (UK)'), ('VI', 'Virgin Islands (US)'), ('VN', 'Vietnam'), ('VU', 'Vanuatu'), ('WF', 'Wallis & Futuna'), ('WS', 'Samoa (western)'), ('YE', 'Yemen'), ('YT', 'Mayotte'), ('ZA', 'South Africa'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(default='New Customer', max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='customer',
            name='phone',
            field=models.CharField(default=b'', max_length=32, verbose_name='phone', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='customer',
            name='zip_code',
            field=models.CharField(default=b'', max_length=32, verbose_name='ZIP Code', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='customergroup',
            name='name',
            field=models.CharField(default='New Group', unique=True, max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='description',
            field=models.CharField(default='New Device', max_length=128, verbose_name='description'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='password',
            field=models.CharField(default=b'', max_length=32, verbose_name='password', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='purchased_on',
            field=models.DateField(null=True, verbose_name='Date Purchased', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='sn',
            field=models.CharField(default=b'', max_length=32, verbose_name='Serial Number', blank=True, validators=[servo.validators.sn_validator]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='username',
            field=models.CharField(default=b'', max_length=32, verbose_name='username', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='device',
            name='warranty_status',
            field=models.CharField(default=b'NA', max_length=3, verbose_name='Warranty Status', choices=[(b'QP', 'Quality Program'), (b'CS', 'Customer Satisfaction'), (b'ALW', 'Apple Limited Warranty'), (b'APP', 'AppleCare Protection Plan'), (b'CC', 'Custom Bid Contracts'), (b'CBC', 'Custom Bid Contracts'), (b'WTY', "3'rd Party Warranty"), (b'OOW', 'Out Of Warranty (No Coverage)'), (b'NA', 'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gsxaccount',
            name='password',
            field=models.CharField(default=b'', max_length=256, verbose_name='Password', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='customer_address',
            field=models.CharField(max_length=255, null=True, verbose_name='Address', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='customer_email',
            field=models.CharField(max_length=128, null=True, verbose_name='Email', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='customer_name',
            field=models.CharField(default='Walk-in', max_length=255, verbose_name='Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='customer_phone',
            field=models.CharField(max_length=128, null=True, verbose_name='Phone', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_method',
            field=models.IntegerField(default=0, verbose_name='Payment Method', editable=False, choices=[(0, 'No Charge'), (1, 'Cash'), (2, 'Invoice'), (3, 'Credit Card'), (4, 'Mail payment'), (5, 'Online payment')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='description',
            field=models.TextField(default=b'', verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='notes',
            field=models.TextField(default=b'9:00 - 18:00', help_text='Will be shown on print templates', verbose_name='Notes', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='phone',
            field=models.CharField(default=b'', max_length=32, verbose_name='phone', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='title',
            field=models.CharField(default='New Location', max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='zip_code',
            field=models.CharField(default=b'', max_length=8, verbose_name='ZIP Code', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='payment',
            name='method',
            field=models.IntegerField(default=0, verbose_name='Payment Method', choices=[(0, 'No Charge'), (1, 'Cash'), (2, 'Invoice'), (3, 'Credit Card'), (4, 'Mail payment'), (5, 'Online payment')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(default=b'', verbose_name='Description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='property',
            name='type',
            field=models.CharField(default=(b'customer', 'Customer'), max_length=32, verbose_name='type', choices=[(b'customer', 'Customer'), (b'order', 'Order'), (b'product', 'Product')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='purchaseorderitem',
            name='description',
            field=models.TextField(default=b'', verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='queue',
            name='description',
            field=models.TextField(verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='repair',
            name='replacement_sn',
            field=models.CharField(default=b'', help_text='Serial Number of replacement part', max_length=18, verbose_name='New serial number', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceorderitem',
            name='description',
            field=models.TextField(default=b'', verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='serviceorderitem',
            name='price_category',
            field=models.CharField(default=(b'warranty', 'Warranty'), max_length=32, verbose_name='Price category', choices=[(b'warranty', 'Warranty'), (b'exchange', 'Exchange Price'), (b'stock', 'Stock Price')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='status',
            name='description',
            field=models.TextField(null=True, verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='status',
            name='title',
            field=models.CharField(default='New Status', max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='title',
            field=models.CharField(default='New Tag', unique=True, max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='type',
            field=models.CharField(max_length=32, verbose_name='type', choices=[(b'device', 'Device'), (b'order', 'Order'), (b'note', 'Note'), (b'other', 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='gsx_password',
            field=models.CharField(default=b'', max_length=256, verbose_name='Password', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='locale',
            field=models.CharField(default=b'da_DK.UTF-8', help_text='Select which language you want to use Servo in.', max_length=32, verbose_name='language', choices=[(b'da_DK.UTF-8', 'Danish'), (b'nl_NL.UTF-8', 'Dutch'), (b'en_US.UTF-8', 'English'), (b'et_EE.UTF-8', 'Estonian'), (b'fi_FI.UTF-8', 'Finnish'), (b'sv_SE.UTF-8', 'Swedish')]),
            preserve_default=True,
        ),
    ]
