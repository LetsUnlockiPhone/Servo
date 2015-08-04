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

import os
import re
import phonenumbers
from gsxws.core import validate
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


def phone_validator(val):
    try:
        phonenumbers.parse(val, settings.INSTALL_COUNTRY)
    except phonenumbers.NumberParseException:
        raise ValidationError(_('%s is not a valid phone number') % val)

def apple_sn_validator(val):
    if validate(val.upper()) not in ('serialNumber', 'alternateDeviceId',):
        raise ValidationError(_(u'%s is not a valid serial or IMEI number') % val)

def sn_validator(val):
    if not re.match(r'^\w*$', val):
        raise ValidationError(_('Serial numbers may only contain letters and numbers'))

def file_upload_validator(val):
    allowed = ['.pdf', '.zip', '.doc', '.jpg', '.jpeg', '.png', '.txt', '.mov', '.m4v']
    ext = os.path.splitext(val.name)[1].lower()
    if not ext in allowed:
        raise ValidationError(_('Invalid file type: %s') % ext)
