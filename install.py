#! /usr/bin/env python

import os
import socket
import requests
from string import Template
from subprocess import call

from servo.models import Location, User

default_hostname = socket.gethostname()
tpl_url = 'https://gist.githubusercontent.com/filipp/cba2ffecd0d5790f7245/raw/'

print("** Creating local configuration file **")

args = {}
args['secret_key'] = os.urandom(32).encode('base-64').strip()
args['install_country'] = raw_input('Country [SE]: ') or 'SE'
args['install_locale'] = raw_input('Locale [sv_SE.UTF-8]: ') or 'sv_SE.UTF-8'
args['install_language'] = raw_input('Language [sv]: ') or 'sv'
args['timezone'] = raw_input('Timezone [Europe/Stockholm]: ') or 'Europe/Stockholm'
args['install_id'] = raw_input('Installation ID [22]: ') or '22'

args['hostname'] = raw_input('Hostname [%s]' % default_hostname) or default_hostname
args['dbhost']   = raw_input('Database host [localhost]: ') or 'localhost'
args['dbname']   = raw_input('Database [servo]: ') or 'servo'
args['dbuser']   = raw_input('DB user [servo]: ') or 'servo'
args['dbpwd']    = raw_input('DB password []: ') or ''

raw = requests.get(tpl_url).text
template = Template(raw)

s = template.substitute(**args)

call(['createuser', args['dbuser'], '-U', 'pgsql'])
call(['createdb', args['dbname'], '-O', args['dbuser'], '-U', 'pgsql'])

fh = open('local_settings.py', 'w')
fh.write(s)
fh.close()

loc = {}

print("** Setting up database tables **")
call(['./manage.py', 'migrate', '--no-initial-data'])

print("** Creating Super User **")
call(['./manage.py', 'createsuperuser'])

print("** Creating initial Service Location **")
loc['title']    = raw_input('Name [PretendCo Inc]: ') or 'PretendCo Inc'
loc['email']    = raw_input('Email [service@pretendo.com]: ') or 'service@pretendo.com'
loc['phone']    = raw_input('Phone [123456789]: ') or '123456789'
loc['address']  = raw_input('Address [Somestreet 1]: ') or 'Somestreet 1'
loc['zip_code'] = raw_input('Postal code [1234]: ') or '1234'
loc['city']     = raw_input('City [Stockholm]: ') or 'Stockholm'

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
