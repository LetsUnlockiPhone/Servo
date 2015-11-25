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

![The Obligatory Screenshot](http://www.servoapp.com/img/screenshots/940/order1.png)


System Requirements
===================
The application is written in Python on top of the excellent [Django web framework](https://www.djangoproject.com) and depends on the latest stable versions of the following components for operation:

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

Next, run the installation script:

	$ ./install.py

For testing, you can run Servo without any extra setup:

	$ cd my_servo_folder
	$ python ./manage.py runserver

If you want to run rules, set ENABLE_RULES = True and start the worker task:

    $ celery -A servo worker -B -l info -s /tmp/celerybeat-schedule

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
End-user documentation for the system is available [here](https://docs.servoapp.com). A user-friendly list of changes is published [here](https://docs.servoapp.com/changelog/).


FAQ
===
- **Q: Why use Django?**
- A: Because it works. Django also has the best documentation of any framework I've seen (especially coming from PHP and Zend Framework)
- **Q: Why is Servo open-source?**
- A: Because it's a mission-critical application and open-sourcing it means that companies will always have access to it.

