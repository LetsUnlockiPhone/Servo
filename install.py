#! /usr/bin/env python

import os
import socket
import requests
from string import Template
from subprocess import call

args = {}
args['hostname'] = socket.gethostname()
args['secret_key'] = os.urandom(32).encode('base-64').strip()
args['install_country'] = raw_input('Country [SE]: ') or 'SE'
args['install_locale'] = raw_input('Locale [sv_SE.UTF-8]: ') or 'sv_SE.UTF-8'
args['install_language'] = raw_input('Language [sv]: ') or 'sv'
args['timezone'] = raw_input('Timezone [Europe/Stockholm]: ') or 'Europe/Stockholm'
args['install_id'] = raw_input('Installation ID [22]: ') or '22'

args['dbhost']  = raw_input('Database host [localhost]: ') or 'localhost'
args['dbname']  = raw_input('Database [servo]: ') or 'servo'
args['dbuser']  = raw_input('DB user [servo]: ') or 'servo'
args['dbpwd']   = raw_input('DB password []: ') or ''

tpl_url = 'https://gist.githubusercontent.com/filipp/cba2ffecd0d5790f7245/raw/'
raw = requests.get(tpl_url).text
template = Template(raw)

s = template.substitute(**args)

call(['createuser', args['dbuser'], '-U', 'pgsql'])
call(['createdb', args['dbname'], '-O', args['dbuser'], '-U', 'pgsql'])

fh = open('local_settings.py', 'w')
fh.write(s)
fh.close()

call(['./manage.py', 'migrate', '--no-initial-data'])
call(['./manage.py', 'createsuperuser'])
