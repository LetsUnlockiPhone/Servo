# -*- coding: utf-8 -*-

import os
import re
import socket
from datetime import timedelta
from django.contrib.messages import constants as messages

DEBUG = False
TEMPLATE_DEBUG = DEBUG

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

BASE_DIR = os.path.dirname(__file__)
APP_DIR  = os.path.join(BASE_DIR, 'servo')

ADMINS = (
    ('ServoApp Support', 'support@servoapp.com'),
)

MANAGERS = ADMINS

LANGUAGES = (
    ('da', 'Danish'),
    ('nl', 'Dutch'),
    ('en', 'English'),
    ('et', 'Estonian'),
    ('fi', 'Finnish'),
    ('sv', 'Swedish'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True
USE_THOUSAND_SEPARATOR = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/files/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.dirname(os.path.join(BASE_DIR, 'static'))

# Additional locations of static files
STATICFILES_DIRS = (
    'static',
)

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'servo.lib.middleware.LoginRequiredMiddleware',
    'servo.lib.middleware.TimezoneMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'servo.urls.default'
SESSION_SERIALIZER = 'servo.lib.utils.SessionSerializer'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(APP_DIR, 'templates'),
    os.path.join(BASE_DIR, 'uploads'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sessions',
    #'debug_toolbar',
    'rest_framework',
    'rest_framework.authtoken',
    'mptt', 'bootstrap3',
    'servo',
)

AUTH_USER_MODEL = 'servo.User'
AUTH_PROFILE_MODULE = 'servo.UserProfile'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'stderr': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

FILE_UPLOAD_HANDLERS = ("django_excel.ExcelMemoryFileUploadHandler",
                        "django_excel.TemporaryExcelFileUploadHandler",)

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.contrib.messages.context_processors.messages",
)

EXEMPT_URLS = []

LOGIN_URL   = '/login/'
LOGOUT_URL  = '/logout/'

# URLs that should work without logging in
LOGIN_EXEMPT_URLS = [
    LOGIN_URL.lstrip('/'),
    'register/$',
    'checkin/',
    'barcode/',
    'api/messages/',
    'api/status/',
    'api/warranty/',
    'api/orders/',
    'api/notes/',
    'api/users/',
    'api/customers/',
    'api/devices/'
]

# 404 URLs that should be ignored
IGNORABLE_404_URLS = [
    re.compile(r'favicon\.ico')
]

TEST_RUNNER = 'servo.tests.NoDbTestRunner'

EMAIL_HOST = 'mail.servoapp.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[Servo] '
DEFAULT_FROM_EMAIL = 'support@servoapp.com'
SERVER_EMAIL = 'servo@' + socket.gethostname()

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

ENABLE_RULES = False
TIMEZONE = 'Europe/Helsinki'
BACKUP_DIR  = os.path.join(BASE_DIR, 'backups')

GSX_CERT = 'uploads/settings/gsx_cert.pem'
GSX_KEY  = 'uploads/settings/gsx_key.pem'

os.environ['GSX_CERT'] = GSX_CERT
os.environ['GSX_KEY']  = GSX_KEY

CELERYBEAT_SCHEDULE = {
    'check_mail': {
        'task': 'servo.tasks.check_mail',
        'schedule': timedelta(seconds=300),
    },
}

from local_settings import *
