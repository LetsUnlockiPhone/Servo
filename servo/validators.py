# -*- coding: utf-8 -*-

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
