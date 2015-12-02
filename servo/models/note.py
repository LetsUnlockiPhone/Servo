# -*- coding: utf-8 -*-

import re
import base64
import urllib
import chardet
import html2text
from email.header import decode_header

from django.db import models, IntegrityError

from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from django.core.mail import send_mail, EmailMessage
from django.contrib.contenttypes.fields import GenericRelation

from django.template.defaultfilters import truncatechars
from django.db.models.signals import pre_delete, post_save

from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey

from servo import defaults
from servo.lib.shorturl import from_time

from servo.models.order import Order
from servo.models.account import User
from servo.models.customer import Customer
from servo.models.escalations import Escalation
from servo.models.common import Configuration, Tag, Attachment, Event


SMS_ENCODING = 'ISO-8859-15'
COOKIE_REGEX = r'\(SRO#([\w/]+)\).*$'


class UnsavedForeignKey(models.ForeignKey):
    # A ForeignKey which can point to an unsaved object
    allow_unsaved_instance_assignment = True


def clean_phone_number(number):
    return re.sub(r'[\+\s\-]', '', number).strip()


def validate_phone_number(number):
    match = re.match(r'([\+\d]+$)', number)
    if match:
        return match.group(1).strip()
    else:
        raise ValidationError(_(u'%s is not a valid phone number') % number)


class Note(MPTTModel):

    T_NOTE          = 0
    T_PROBLEM       = 1
    T_ESCALATION    = 2

    subject = models.CharField(
        blank=True,
        max_length=255,
        default=defaults.subject,
        verbose_name=_('Subject'),
    )

    body = models.TextField(verbose_name=_('Message'))

    code = models.CharField(
        unique=True,
        max_length=9,
        editable=False,
        default=from_time
    )
    sender = models.CharField(
        default='',
        max_length=255,
        verbose_name=_('From')
    )
    recipient = models.CharField(
        blank=True,
        default='',
        max_length=255,
        verbose_name=_('To')
    )
    customer = models.ForeignKey(Customer, null=True, blank=True)
    escalation = UnsavedForeignKey(Escalation, null=True, editable=False)
    labels = models.ManyToManyField(Tag, blank=True, limit_choices_to={'type': 'note'})

    events = GenericRelation(Event)
    attachments = GenericRelation(Attachment, null=True, blank=True)
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies'
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    sent_at = models.DateTimeField(null=True, editable=False)
    order = models.ForeignKey(Order, null=True, blank=True)

    is_reported = models.BooleanField(
        default=False,
        verbose_name=_("Report")
    )
    is_read = models.BooleanField(
        default=True,
        editable=False,
        verbose_name=_("Read")
    )
    is_flagged = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=_("Flagged")
    )

    TYPES = (
        (T_NOTE,        _('Note')),
        (T_PROBLEM,     _('Problem')),
        (T_ESCALATION,  _('Escalation')),
    )

    type = models.IntegerField(
        blank=True,
        default=T_NOTE,
        choices=TYPES,
        verbose_name=_('Type')
    )

    objects = TreeManager()

    def __render__(self, tpl, ctx):
        from django import template
        tpl = template.Template(tpl)
        return tpl.render(template.Context(ctx))

    def render_subject(self, ctx):
        """
        Renders this Markdown body
        """
        self.subject = self.__render__(self.subject, ctx)
        return self.subject

    def render_body(self, ctx):
        """
        Renders this Markdown body
        """
        self.body = self.__render__(self.body, ctx)
        return self.body

    def add_reply(self, note):
        note.parent = self
        note.order = self.order
        note.escalation = self.escalation
        
    def zip_attachments(self):
        pass

    def get_default_sender(self):
        return Configuration.get_default_sender(self.created_by)

    def get_sender_choices(self):
        """
        Returns the options for this note's senders
        """
        choices = []
        addresses = []
        user = self.created_by
        loc = user.location
        def_email = self.get_default_sender()

        if user.email:
            user_choice = (user.email, u'%s <%s>' % (user.get_name(), user.email),)
            choices.append(user_choice)
            addresses.append(user.email)

        if loc.email and loc.email not in addresses:
            loc_choice = (loc.email, u'%s <%s>' % (loc.title, loc.email),)
            choices.append(loc_choice)
            addresses.append(loc.email)

        if def_email and def_email not in addresses:
            def_choice = (def_email, _(u'Default Address <%s>') % def_email,)
            choices.append(def_choice)

        return choices

    def quote(self):
        return "> " + self.body

    def unquote(self):
        return re.sub(r'^>.*', '', self.body, flags=re.MULTILINE).strip()

    def clean_subject(self):
        return re.sub(COOKIE_REGEX, '', self.subject)

    def get_excluded_emails(self):
        """
        Returns a list of email addresses that should not be contacted
        """
        if not cache.get('nomail'):
            User.refresh_nomail()

        return cache.get('nomail')

    def get_classes(self):
        """
        Returns the appropriate CSS classes for this note
        """
        classes = list()

        if not self.is_read:
            classes.append('info')

        if self.is_reported:
            classes.append('success')

        if self.is_flagged:
            classes.append('warning')

        return ' '.join(classes)

    def find_parent(self, txt):
        """
        Finds the parent of this note
        """
        cookie = re.search(r'\(SRO#([\w/]+)\)', txt)

        if not cookie:
            return

        parent_code, order_code = cookie.group(1).split('/')

        try:
            parent = Note.objects.get(code=parent_code)
            self.parent = parent
            self.recipient = parent.sender
            self.order_id = parent.order_id
        except Note.DoesNotExist:
            # original note has been deleted
            self.order = Order.objects.get(url_code=order_code)

    @classmethod
    def from_email(cls, msg, user):
        """
        Creates a new Note from an email message
        """
        sender = decode_header(msg['From'])
        detected = chardet.detect(sender[0][0]).get('encoding')
        sender = [i[0].decode(i[1] or detected) for i in sender]
        sender = ' '.join(sender)

        note = cls(sender=sender, created_by=user)

        note.is_read = False
        note.is_reported = False
        note.recipient = msg['To']

        subject = decode_header(msg['Subject'])[0]
        detected = chardet.detect(subject[0]).get('encoding')
        note.subject = subject[0].decode(subject[1] or detected)

        note.find_parent(note.subject)

        for part in msg.walk():
            t, s = part.get_content_type().split('/', 1)
            charset = part.get_content_charset() or "latin1"

            if t == "text":
                payload = part.get_payload(decode=True)
                note.body = unicode(payload, str(charset), "ignore")
                if s == "html":
                    h = html2text.HTML2Text()
                    h.ignore_images = True
                    note.body = h.handle(note.body)
            else:
                note.save()
                if part.get_filename():
                    filename = unicode(part.get_filename())
                    payload = part.get_payload()
                    content = base64.b64decode(payload)
                    content = ContentFile(content, filename)
                    attachment = Attachment(content=content, content_object=note)
                    attachment.save()
                    attachment.content.save(filename, content)
                    note.attachments.add(attachment)

        if not note.parent:
            # cookie not found in the subject, let's try the body...
            note.find_parent(note.body)

        note.save()

        return note

    def get_sender_name(self):
        name = self.created_by.get_full_name()
        if not name:
            name = self.created_by.username

        return name

    def get_flags(self):
        return ['unread', 'flagged', 'reported']

    def get_reported_title(self):
        return _("As Unreported") if self.is_reported else _("As Reported")

    def get_read_title(self):
        return _("As Unread") if self.is_read else _("As Read")

    def get_flagged_title(self):
        return _("As Unflagged") if self.is_flagged else _("As Flagged")

    def mailto(self):
        """
        Returns the email recipients of this note
        Don't use validate_email because addresses may also be in 
        Name <email> format (replies to emails)
        """
        to = []
        recipients = [r.strip() for r in self.recipient.split(',')]
        for r in recipients:
            m = re.search(r'([\w\.\-_]+@[\w\.\-_]+)', r, re.IGNORECASE)
            if m:
                to.append(m.group(0))

        return ','.join(to)

    def get_indent(self):
        return (self.level*20)+10

    def notify(self, action, message, user):
        e = Event(content_object=self, action=action)
        e.description = message
        e.triggered_by = user
        e.save()

    def get_edit_url(self):
        if self.order:
            return reverse('orders-edit_note', args=[self.order.pk, self.pk])

    def has_sent_message(self, recipient):
        r = self.message_set.filter(recipient=recipient)
        return r.exclude(status='FAILED').exists()

    def send_mail(self, user):
        """Sends this note as an email"""
        mailto = self.mailto()

        # Only send the same note once
        if self.has_sent_message(mailto):
            raise ValueError(_('Already sent message to %s') % mailto)

        config = Configuration.conf()
        smtp_host = config.get('smtp_host').split(':')
        settings.EMAIL_HOST = smtp_host[0]

        if len(smtp_host) > 1:
            settings.EMAIL_PORT = int(smtp_host[1])

        settings.EMAIL_USE_TLS = config.get('smtp_ssl')
        settings.EMAIL_HOST_USER = str(config.get('smtp_user'))
        settings.EMAIL_HOST_PASSWORD = str(config.get('smtp_password'))

        headers = {}
        headers['Reply-To'] = self.sender
        headers['References'] = '%s.%s' % (self.code, self.sender)
        subject = u'%s (SRO#%s)' % (self.subject, self.code)

        if self.order:
            # Encode the SO code so that we can match replies to the SO
            # even if the original note has been deleted
            subject = u'%s (SRO#%s/%s)' % (self.subject,
                                           self.code,
                                           self.order.url_code)

        recipients = mailto.split(',')

        msg = EmailMessage(subject,
                           self.body,
                           self.sender,
                           recipients,
                           headers=headers)

        for f in self.attachments.all():
            msg.attach_file(f.content.path)
        
        msg.send()

        for r in recipients:
            msg = Message(note=self, recipient=r, created_by=user, body=self.body)
            msg.sent_at = timezone.now()
            msg.sender = self.sender
            msg.status = 'SENT'
            msg.save()

        message = _(u'Message sent to %s') % mailto
        self.notify('email_sent', message, user)
        return message

    def send_sms_smtp(self, config, recipient):
        """
        Sends SMS through SMTP gateway
        """
        recipient = recipient.replace(' ', '')
        settings.EMAIL_HOST = config.get('smtp_host')
        settings.EMAIL_USE_TLS = config.get('smtp_ssl')
        settings.EMAIL_HOST_USER = config.get('smtp_user')
        settings.EMAIL_HOST_PASSWORD = config.get('smtp_password')

        send_mail(recipient, self.body, self.sender, [config['sms_smtp_address']])

    def send_sms_builtin(self, recipient, sender=None):
        """
        Sends SMS through built-in gateway
        """
        if not settings.SMS_HTTP_URL:
            raise ValueError(_('System is not configured for built-in SMS support.'))

        if sender is None:
            location = self.created_by.location
            sender = location.title

        data = urllib.urlencode({
            'username'  : settings.SMS_HTTP_USERNAME,
            'password'  : settings.SMS_HTTP_PASSWORD,
            'numberto'  : recipient.replace(' ', ''),
            'numberfrom': sender.encode(SMS_ENCODING),
            'message'   : self.body.encode(SMS_ENCODING),
        })

        from ssl import _create_unverified_context
        f = urllib.urlopen(settings.SMS_HTTP_URL, data, context=_create_unverified_context())
        return f.read()

    def send_sms(self, number, user):
        """
        Sends message as SMS
        """
        number = validate_phone_number(number)

        if self.has_sent_message(number):
            raise ValueError(_('Already sent message to %s') % number)

        conf = Configuration.conf()
        sms_gw = conf.get('sms_gateway')

        if not sms_gw:
            raise ValueError(_("SMS gateway not configured"))
        
        msg = Message(note=self, recipient=number, created_by=user, body=self.body)
        
        if sms_gw == 'hqsms':
            from servo.messaging.sms import HQSMSProvider
            HQSMSProvider(number, self, msg).send()

        if sms_gw == 'jazz':
            from servo.messaging.sms import SMSJazzProvider
            SMSJazzProvider(number, self, msg).send()
            #self.send_sms_jazz(number, conf.get('sms_http_sender', ''), msg)

        if sms_gw == 'http':
            from servo.messaging.sms import HttpProvider
            HttpProvider(self, number).send()

        if sms_gw == 'smtp':
            gw_address = conf.get('sms_smtp_address')

            if not gw_address:
                raise ValueError('Missing SMTP SMS gateway address')

            self.send_sms_smtp(conf, number)

        if sms_gw == 'builtin':
            self.send_sms_builtin(number)

        msg.method  = 'SMS'
        msg.status  = 'SENT'
        msg.sent_at = timezone.now()
        msg.save()

        message = _('Message sent to %s') % number
        self.notify('sms_sent', message, self.created_by)
        return message

    def send_and_save(self, user):
        """
        The main entry point to the sending logic
        """
        from django.utils.encoding import force_text
        messages = list()
        recipients = [r.strip() for r in self.recipient.split(',')]

        for r in recipients:
            try:
                messages.append(self.send_sms(r, user))
            except (ValidationError, IntegrityError), e:
                pass

        if self.mailto():
            messages.append(self.send_mail(user))

        esc = self.escalation

        if esc and esc.pk and esc.issue_type:
            if esc.submitted_at is None:
                esc.submit()
                messages.append(_('Escalation %s created') % esc.escalation_id)
            else:
                esc.update(self.body)
                messages.append(_('Escalation %s updated') % esc.escalation_id)

        self.save()

        if len(messages) < 1:   
            messages = [_('Note saved')]

        return ', '.join([force_text(m) for m in messages])

    def get_absolute_url(self):
        if self.order:
            return "%s#note-%d" % (self.order.get_absolute_url(), self.pk)
        else:
            return "/notes/saved/%d/view/" % self.pk

    def __unicode__(self):
        return str(self.pk)

    class Meta:
        app_label = "servo"
        get_latest_by = "created_at"


class Message(models.Model):
    """
    A note being sent by some method (SMS, email, escalation).
    Only one sender and recipient per message
    Keeping this separate from Note so that we can send and track
    messages separately from Notes
    """
    note = models.ForeignKey(Note)
    code = models.CharField(unique=True, max_length=36, default=defaults.uid)
    created_by = models.ForeignKey(User)
    sender = models.CharField(max_length=128)
    recipient = models.CharField(max_length=128)
    body = models.TextField()
    sent_at = models.DateTimeField(null=True)
    received_at = models.DateTimeField(null=True)
    STATUSES = (
        ('SENT',      'SENT'),
        ('DELIVERED', 'DELIVERED'),
        ('RECEIVED',  'RECEIVED'),
        ('FAILED',    'FAILED'),
    )
    status = models.CharField(max_length=16, choices=STATUSES)
    METHODS = (
        ('EMAIL', 'EMAIL'),
        ('SMS',   'SMS'),
        ('GSX',   'GSX'),
    )
    method = models.CharField(
        max_length=16,
        choices=METHODS,
        default=METHODS[0][0]
    )
    error = models.TextField()
    
    def send(self):
        result = None
        self.recipient = self.recipient.strip()

        try:
            validate_phone_number(self.recipient)
            result = self.send_sms()
        except ValidationError:
            pass

        try:
            validate_email(self.recipient)
            result = self.send_mail()
        except ValidationError:
            pass

        self.save()
        return result

    class Meta:
        app_label = "servo"
        unique_together = ('note', 'recipient')


@receiver(pre_delete, sender=Note)
def clean_files(sender, instance, **kwargs):
    instance.attachments.all().delete()


@receiver(post_save, sender=Note)
def note_saved(sender, instance, created, **kwargs):
    if created and instance.order:
        order = instance.order
        user = instance.created_by

        if user is not order.user:
            msg = truncatechars(instance.body, 75)
            order.notify("note_added", msg, user)

