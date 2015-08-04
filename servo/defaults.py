# -*- coding: utf-8 -*-
# Copyright (c) 2013, First Party Software
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
# SUCH DAMAGE.

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
