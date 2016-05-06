#! /usr/bin/env python

import os
import socket
import django
import requests
from string import Template
from subprocess import call

default_hostname = socket.gethostname()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

tpl_url = 'https://gist.githubusercontent.com/filipp/cba2ffecd0d5790f7245/raw/'

fh = open('local_settings.py', 'w')

print("** Creating local configuration file **")
args = {}
args['dbadmin']    = raw_input('DB admin username [pgsql]: ') or 'pgsql'
args['secret_key'] = os.urandom(32).encode('base-64').strip()
args['install_locale'] = raw_input('1/10 Locale [sv_SE.UTF-8]: ') or 'sv_SE.UTF-8'
default_country = args['install_locale'].split('_')[0]
args['install_country'] = raw_input('2/10 Country [%s]: ' % default_country) or default_country
default_lang = args['install_locale'].split('_')[1][:2]
args['install_language'] = raw_input('3/10 Language [%s]: ' % default_lang) or default_lang
args['timezone'] = raw_input('4/10 Timezone [Europe/Stockholm]: ') or 'Europe/Stockholm'
args['install_id'] = raw_input('5/10 Installation ID [22]: ') or '22'
args['hostname'] = raw_input('6/10 Hostname [%s]: ' % default_hostname) or default_hostname
args['dbhost']   = raw_input('7/10 Database host [localhost]: ') or 'localhost'
args['dbname']   = raw_input('8/10 Database [servo]: ') or 'servo'
args['dbuser']   = raw_input('9/10 DB user [servo]: ') or 'servo'
args['dbpwd']    = raw_input('10/10 DB password []: ') or ''

raw = requests.get(tpl_url).text
template = Template(raw)

s = template.substitute(**args)

call(['createuser', args['dbuser'], '-U', args['dbadmin']])
call(['createdb', args['dbname'], '-O', args['dbuser'], '-U', args['dbadmin']])

fh.write(s)
fh.close()

print("** Setting up database tables **")
call(['./manage.py', 'migrate'])
call(['psql', '-c', 'ALTER SEQUENCE servo_order_id_seq RESTART WITH 12345', args['dbname'], args['dbuser']])

print("** Creating Super User **")
call(['./manage.py', 'createsuperuser'])

loc = {}
django.setup() # To avoid django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
print("** Creating initial Service Location **")
loc['title']    = raw_input('1/6 Name [PretendCo Inc]: ') or 'PretendCo Inc'
loc['email']    = raw_input('2/6 Email [service@pretendo.com]: ') or 'service@pretendo.com'
loc['phone']    = raw_input('3/6 Phone [123456789]: ') or '123456789'
loc['address']  = raw_input('4/6 Address [Somestreet 1]: ') or 'Somestreet 1'
loc['zip_code'] = raw_input('5/6 Postal code [1234]: ') or '1234'
loc['city']     = raw_input('6/6 City [Stockholm]: ') or 'Stockholm'

from servo.models.common import Location
from servo.models.account import User

first_loc = Location(**loc)
first_loc.save()
su = User.objects.filter(pk=1).update(location=first_loc)

print("** Creating self-signed SSL certificate **")
subj = "/C=%s/ST=%s/L=%s/O=%s/OU=%s/CN=%s" % (
    args['install_country'],
    loc['city'],
    loc['city'],
    loc['title'],
    loc['title'],
    args['hostname']
)

call(['openssl', 'req', '-nodes', '-x509', '-newkey', 'rsa:2048',
    '-days', '365', '-subj', subj,
    '-keyout', 'servo.key', '-out', 'servo.crt'])

print("Your Servo installation is ready for action at https://%s" % args['hostname'])
