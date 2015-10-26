# -*- coding: utf-8 -*-

import re
import urllib
from hashlib import md5
from ssl import _create_unverified_context

from django.conf import settings
from django.utils.translation import ugettext as _

from servo.models.common import Configuration


class BaseSMSProvider:
    def __init__(self, recipient, note, msg):
        self.conf = Configuration.conf()

        if not self.conf.get('sms_http_sender'):
            raise ValueError(_("SMS sender not configured"))

        if len(recipient) < 8:
            recipient = '372' + recipient
        
        recipient = re.sub(r'[\+\s\-]', '', recipient)
        self.recipient = recipient.lstrip('+')
        self.note = note
        self.msg = msg

        self.sender = self.conf['sms_http_sender']
        self.body = self.note.body.encode('utf-8')


class SMSJazzProvider:
    """
    SMS Jazz gateway provider
    Used mainly by Estonian AASPs, hence default prefix of 372
    """
    URL = 'https://www.smsjazz.net/SMSjazzAPI/sendsms.php'

    STATUSES = {
        '1' : ('DELIVERED', 'SMS message is delivered to mobile phone'),
        '2' : ('FAILED', 'SMS message has failed and is not delivered to mobile phone'),
        '4' : ('SENT', 'SMS message is buffered and is waiting to be delivered to mobile phone'),
        '8' : ('SENT', 'SMS message is buffered and is waiting to be delivered to mobile phone'),
        '16': ('FAILED', 'Error in sender/receiver/message parameters'),
        '32': ('SENT', ''),
    }

    def  __init__(self, recipient, note, msg):
        if len(recipient) < 8:
            recipient = '372' + recipient
        
        recipient = re.sub(r'[\+\s\-]', '', recipient)
        self.recipient = recipient.lstrip('+')
        self.note = note
        self.msg = msg

    def send(self):
        """
        Sends SMS through SMS Jazz Gateway
        """
        conf = Configuration.conf()

        if not conf.get('sms_http_sender'):
            raise ValueError(_("SMS sender name not configured"))

        body = self.note.body.encode('utf-8')
        sender = conf.get('sms_http_sender')
        pwhash = md5(conf['sms_http_password']).hexdigest()
        checksum = md5(body + self.recipient.encode('ascii') + pwhash).hexdigest()

        params = {
            'username'  : conf['sms_http_user'],
            'password'  : pwhash,
            'message'   : body,
            'sender'    : sender.encode('ascii', 'replace'),
            'receiver'  : self.recipient,
            'charset'   : 'UTF8',
            'checksum'  : checksum,
        }

        if self.msg:
            dlruri = '/api/messages/?id={0}&status=%status%'.format(self.msg.code)
            dlruri = settings.SERVO_URL + dlruri
            params['dlruri'] = dlruri

        params = urllib.urlencode(params)
        r = urllib.urlopen(self.URL, params, context=_create_unverified_context()).read()

        if not '1:OK' in r:
            raise ValueError(_('Failed to send message to %s') % self.recipient)


class HQSMSProvider(BaseSMSProvider):
    """
    HQSMS Gateway Provider.
    API docs: http://www.hqsms.com/media/page/docs/HQSMS_https.pdf
    """
    URL        = "https://api.smsapi.com/sms.do"
    BACKUP_URL = "https://api2.smsapi.com/sms.do"

    ERRORS = {
        "ERROR:13"  : _("Lack of valid phone numbers (invalid or blacklisted numbers)"),
        "ERROR:14"  : _("Wrong sender name"),
        "ERROR:19"  : _("Too many messages in one request"),
        "ERROR:52"  : _("Too many attempts of sending messages to one number (maximum 10 attempts whin 60s)"),
        "ERROR:102" : _("Invalid username or password"),
        "ERROR:103" : _("Insufficient credits on your account"),
        "ERROR:200" : _("Unsuccessful message submission"),
        "ERROR:201" : _("Internal system error"),
        "ERROR:999" : _("Internal system error"),
    }

    STATUSES = {
        '401' : ('NOT_FOUND', 'Wrong ID or report has expired'),
        '402' : ('EXPIRED', 'Messages expired'),
        '403' : ('SENT', 'Message is sent'),
        '404' : ('DELIVERED', 'Message is delivered to recipient'),
        '405' : ('UNDELIVERED', 'Message is undelivered (invalid number, roaming error etc)'),
        '406' : ('FAILED', 'Sending message failed – please report it to us'),
        '407' : ('REJECTED', 'Message is undelivered (invalid number, roaming error etc)'),
        '408' : ('UNKNOWN', 'No report (message may be either delivered or not)'),
        '409' : ('QUEUED', 'Message is waiting to be sent'),
        '410' : ('ACCEPTED', 'Message is delivered to operator'),
    }

    def send(self):
        pwhash = md5(self.conf['sms_http_password']).hexdigest()

        params = {
            'username'  : self.conf['sms_http_user'],
            'password'  : pwhash,
            'message'   : self.body,
            'from'      : self.sender,
            'to'        : self.recipient,
        }

        if self.msg:
            dlruri = settings.SERVO_URL + '/api/messages/?id={0}'.format(self.msg.code)
            params['notify_url'] = dlruri

        params = urllib.urlencode(params)
        r = urllib.urlopen(self.URL, params, context=_create_unverified_context()).read()

        if 'ERROR:' in r:
            raise ValueError(self.ERRORS.get(r, _('Unknown error (%s)') % r))

    def set_status(self, msg):
        pass


class HttpProvider:
    """
    Sends SMS through a HTTP gateway (ie Kannel)
    """
    def send(self, note, number):
        conf = Configuration.conf()

        if not conf.get('sms_http_url'):
            raise ValueError(_("No SMS HTTP gateway defined"))

        params = urllib.urlencode({
            'username'  : conf['sms_http_user'],
            'password'  : conf['sms_http_password'],
            'text'      : note.body.encode('utf8'),
            'to'        : number
        })

        f = urllib.urlopen("%s?%s" % (conf['sms_http_url'], params), context=_create_unverified_context())
        return f.read()
