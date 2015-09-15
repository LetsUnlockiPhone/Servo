# -*- coding: utf-8 -*-

"""
defaults.py
Contains callables for model default values
"""
import uuid
import settings
import local_settings
from decimal import Decimal

from django.db import connection
from django.core.cache import cache

def _get(key):
    cached = cache.get('defaults', {})
    
    if not cached.get(key):
        cursor = connection.cursor()
        cursor.execute("SELECT key, value FROM servo_configuration")
        for r in cursor.fetchall():
            cached[r[0]] = r[1]

        cache.set('defaults', cached)

    return cached.get(key)

def country():
    return local_settings.INSTALL_COUNTRY

def site_id():
    return settings.SITE_ID

def locale():
    return settings.INSTALL_LOCALE

def uid():
    return str(uuid.uuid1()).upper()

def subject():
    return _get('default_subject')

def vat():
    val = _get('pct_vat') or 0.0
    return Decimal(val)

def margin(sum=0.0):
    return _get('pct_margin') or 0.0

def gsx_account():
    return _get('gsx_account')
