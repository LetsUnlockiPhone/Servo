Introduction
============

Servo is a service management system for Authorised Apple Service Providers. It allows you to run your entire service business from within the same interface. Originally created in 2012 it is being used by service providers both large and small all around Europe.

Main features include:

- Flexible workflow management (create separate queues for different types of work, customize statuses and time limits per queue)
- Complete integration with GSX (do warranty and part lookups, create and edit repairs, stocking orders, part returns, etc)
- A rich set of communication tools (two-way email support, SMS sending, GSX escalations, attachment support)
- Inventory management (product categories, stocking per location, bracketed markup)
- Robust customer database (hierarchical customer data, custom fields)
- Fast search
- Statistics and reporting
- Rule-based automation
- Dedicated check-in interface for customers and POS staff
- API for integration with external systems
- It's not FileMaker Pro


System Requirements
===================

The application is written in Python on top of the Django web framework and depends on the latest stable versions of the following components for operation:

- PostgreSQL
- Memcache
- RabbitMQ
- uwsgi
- Python 2.7


Installation
============

Install PostgreSQL, nginx, memcached, rabbitMQ. Then install the necessary Python packages:

    $ pip install -U -r requirements.pip

Then clone the code:

	$ git clone https://github.com/fpsw/Servo.git my_servo_folder
	$ cd my_servo_folder
	$ pip install -U -r requirements.pip


Configuration
=============

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

	SERVO_URL = 'http://123.123.123.123' # External IP for SMS delivery reports (if your SMS provider supports them)

	ENABLE_RULES = True # Whether or not you want to run rules

	TIMEZONE = 'Europe/Helsinki' # Default timezone of this installation (user can choose their own in preferences)

For testing, you can run Servo without any extra setup:

	$ cd my_servo_folder
	$ python ./manage.py runserver

Then fire up your browser and got to http://localhost:8080/


The VMWare Image
================

You can also download a preconfigured VMWare image [here](http://files.servoapp.com/vmware/). Please read the included README files for instructions.


Updating
========

First, back up your database, then:

	$ git pull origin master
	$ ./manage.py migrate --no-initial-data

After which you should restart your Servo instance.


Documentation
=============

End-user documentation for the system is available [here](https://docs.servoapp.com).
