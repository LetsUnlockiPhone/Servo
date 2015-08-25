Introduction
============
Servo is a service management system for Authorised Apple Service Providers.


Installation
============

Install PostgreSQL, nginx, memcached, rabbitMQ. Then install the necessary Python packages:

    $ pip install -U -r requirements.pip

Edit local_settings.py (these are settings specific to your installation):

	import logging
	logging.basicConfig(level=logging.DEBUG)

	DATABASES = {
	    'default': {
	        'ENGINE':   'django.db.backends.postgresql_psycopg2',
	        'NAME':     'MyServoDatabase',
	        'USER':     'MyServoDatabaseUser',
	        'PASSWORD': 'MyServoDatabasePassword',
	        'HOST':     'localhost',
	        'PORT':     '',
	    }
	}

	SECRET_KEY = 'MySuperSecretEncryptionKey'
	TIME_ZONE = 'Europe/Helsinki'

	CACHES = {
	    'default': {
	        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
	        'LOCATION': '127.0.0.1:11211',
	        'TIMEOUT': 60*20,
	        'KEY_PREFIX': 'servo_' # change this if you have other memcache caches running
	    }
	}

	DEBUG = True

	INSTALL_ID = '11' # Service orders will be prefixed with this code
	INSTALL_COUNTRY = 'SE' # Default setting for country
	INSTALL_LOCALE = 'sv_SE.UTF-8' # Default setting for locale
	INSTALL_LANGUAGE = 'se' # Default setting for language

	SERVO_URL = 'http://123.123.123.123' # External IP for SMS delivery reports

	ENABLE_RULES = True # Whether or not you want to run rules

	TIMEZONE = 'Europe/Helsinki' # Default timezone of this installation (user can choose their own in preferences)

For testing, you can run Servo without any extra setup:

	cd my_servo_folder
	python ./manage.py runserver


Documentation
=============
End-user documentation for the system is available [here](https://docs.servoapp.com).
