# -*- coding: utf-8 -*-

import re
import gsxws
import os.path

from decimal import Decimal
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from pytz import common_timezones, country_timezones

from django.contrib.sites.models import Site

from django.db import models
from django.conf import settings

from mptt.managers import TreeManager

from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext_lazy as _

from django.dispatch import receiver
from django.db.models.signals import post_save

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.core.cache import cache

from servo import defaults
from servo.lib.utils import empty
from servo.exceptions import ConfigurationError
from servo.validators import file_upload_validator


# Dict for mapping timezones to countries
TIMEZONE_COUNTRY = {}

for cc in country_timezones:
    timezones = country_timezones[cc]
    for timezone in timezones:
        TIMEZONE_COUNTRY[timezone] = cc


class CsvTable(object):
    def __init__(self, colwidth=20):
        self.rowcount = 0
        self.colwidth = colwidth
        self.body = u''
        self.table = u''
        self.header = u''

    def padrow(self, row):
        r = []
        for c in row:
            r.append(unicode(c).ljust(self.colwidth))

        return r

    def addheader(self, new_header):
        self.rowcount = self.rowcount + 1
        header = self.padrow(new_header)
        self.header = ''.join(header)

    def addrow(self, new_row):
        row = self.padrow(new_row)
        self.body += ''.join(row) + "\n"

    def has_body(self):
        return self.body != ''

    def __unicode__(self):
        self.table = self.header + "\n" + self.body
        return self.table

    def __str__(self):
        return unicode(self).encode('utf-8')


class BaseItem(models.Model):
    """
    Base class for a few generic relationships
    """
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        abstract = True
        app_label = "servo"


class RatedItem(BaseItem):
    rating = models.PositiveIntegerField()


class TimedItem(BaseItem):
    status = models.CharField(max_length=128)
    started_at = models.DateTimeField()
    timeout_at = models.DateTimeField()


class TaggedItem(BaseItem):
    """
    A generic tagged item
    """
    tag = models.CharField(max_length=128)
    slug = models.SlugField()
    color = models.CharField(max_length=8, default="")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.tag)
        super(TaggedItem, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.tag

    class Meta:
        app_label = "servo"
        unique_together = ("content_type", "object_id", "tag",)


class FlaggedItem(BaseItem):
    flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL)


class Event(BaseItem):
    """
    Something that happens
    """
    description = models.CharField(max_length=255)

    triggered_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    triggered_at = models.DateTimeField(auto_now_add=True)
    handled_at = models.DateTimeField(null=True)

    action = models.CharField(max_length=32)
    priority = models.SmallIntegerField(default=1)

    notify_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="notifications" # request.user.notifications
    )

    def save(self, *args, **kwargs):
        saved = super(Event, self).save(*args, **kwargs)

        if settings.ENABLE_RULES is True:
            from servo.tasks import apply_rules
            apply_rules.delay(self)

    def get_status(self):
        from servo.models import Status
        return Status.objects.get(title=self.description)

    def get_icon(self):
        return "events/%s-%s" % (self.content_type, self.action)

    def get_link(self):
        return self.content_object.get_absolute_url()

    def get_class(self):
        return "disabled" if self.handled_at else ""

    def __unicode__(self):
        return self.description

    class Meta:
        ordering = ('priority', '-id',)
        app_label = "servo"


class GsxAccount(models.Model):

    site = models.ForeignKey(
        Site,
        editable=False,
        default=defaults.site_id
    )

    title = models.CharField(max_length=128, default=_("New GSX Account"))
    sold_to = models.CharField(max_length=10, verbose_name=_("Sold-To"))
    ship_to = models.CharField(max_length=10, verbose_name=_("Ship-To"))

    region = models.CharField(
        max_length=3,
        choices=gsxws.GSX_REGIONS,
        verbose_name=_("Region")
    )

    user_id = models.CharField(
        blank=True,
        default='',
        max_length=128,
        verbose_name=_("User ID")
    )

    environment = models.CharField(
        max_length=2,
        verbose_name=_("Environment"),
        choices=gsxws.ENVIRONMENTS,
        default=gsxws.ENVIRONMENTS[0][0]
    )

    @classmethod
    def get_soldto_choices(cls):
        choices = []
        for i in cls.objects.all():
            choice = (i.sold_to, '%s (%s)' % (i.sold_to, i.title))
            choices.append(choice)

        choices = [('', '------------------'),] + choices
        return choices

    @classmethod
    def get_shipto_choices(cls):
        return cls.objects.values_list('ship_to', 'ship_to')


    @classmethod
    def get_default_account(cls):
        from servo.lib.utils import empty
        act_pk = Configuration.conf('gsx_account')

        if empty(act_pk):
            raise ValueError(_('Default GSX account not configured'))

        return GsxAccount.objects.get(pk=act_pk)

    @classmethod
    def get_account(cls, location, queue=None):
        """
        Returns the correct GSX account for the specified user/queue
        """
        try:
            act = location.gsx_accounts.get(sold_to=queue.gsx_soldto)
        except Exception as e:
            act = GsxAccount.get_default_account()

        return act

    @classmethod
    def default(cls, user, queue=None):
        """
        Returns the correct GSX account for
        the specified user/queue and connects to it
        """
        try:
            act = GsxAccount.get_account(user.location, queue)
        except ValueError:
            raise gsxws.GsxError(_('Configuration error'))

        return act.connect(user)

    def connect(self, user, location=None):
        """
        Connects to this GSX Account
        """
        if user.gsx_userid:
            self.user_id = user.gsx_userid

        if location is None:
            timezone = user.location.gsx_tz
        else:
            timezone = location.gsx_tz

        gsxws.connect(user_id=self.user_id,
                      sold_to=self.sold_to,
                      environment=self.environment,
                      timezone=timezone)
        return self

    def test(self):
        """
        Tests that the account details are correct
        """
        gsxws.connect(sold_to=self.sold_to,
                      user_id=self.user_id,
                      environment=self.environment)

    def get_admin_url(self):
        return reverse('admin-edit_gsx_account', args=[self.pk])

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.get_environment_display())

    class Meta:
        app_label = 'servo'
        get_latest_by = 'id'
        ordering = ['title']
        verbose_name = _("GSX Account")
        verbose_name_plural = _("GSX Accounts")
        unique_together = ('sold_to', 'ship_to', 'environment', 'site',)


class Tag(MPTTModel):
    """
    A tag is a simple one-word descriptor for something.
    The type attribute is used to group tags to make them easier
    to associate with different elements
    """
    title = models.CharField(
        unique=True,
        max_length=255,
        default=_('New Tag'),
        verbose_name=_('name')
    )

    TYPES = (
        ('device',  _('Device')),
        ('order',   _('Order')),
        ('note',    _('Note')),
        ('other',   _('Other')),
    )

    type = models.CharField(
        max_length=32,
        choices=TYPES,
        verbose_name=_(u'type')
    )

    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children'
    )

    times_used = models.IntegerField(default=0, editable=False)

    COLORS = (
        ('default',     _('Default')),
        ('success',     _('Green')),
        ('warning',     _('Orange')),
        ('important',   _('Red')),
        ('info',        _('Blue')),
    )

    color = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        choices=COLORS,
        default='default'
    )

    def count_open_orders(self):
        count = self.order_set.filter(state__lt=2).count()
        return count if count > 0 else ''

    def get_admin_url(self):
        return reverse('admin-edit_tag', args=[self.type, self.pk])

    def __unicode__(self):
        return self.title

    objects = TreeManager()

    class Meta:
        app_label = 'servo'
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    class MPTTMeta:
        order_insertion_by = ['title']


class Location(models.Model):
    """
    A Service Location within a company
    """
    site = models.ForeignKey(
        Site,
        editable=False,
        default=defaults.site_id
    )

    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_(u'Name'),
        default=_('New Location'),
    )
    phone = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_('Phone')
    )
    email = models.EmailField(
        blank=True,
        default='',
        verbose_name=_('Email')
    )
    address = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_('Address')
    )
    zip_code = models.CharField(
        blank=True,
        default='',
        max_length=8,
        verbose_name=_('ZIP Code')
    )
    city = models.CharField(
        blank=True,
        default='',
        max_length=16,
        verbose_name=_('City')
    )

    TIMEZONES = tuple((t, t) for t in common_timezones)

    timezone = models.CharField(
        default='UTC',
        max_length=128,
        choices=TIMEZONES,
        verbose_name=_('Time zone')
    )

    # It would make more sense to just store the Ship-To
    # per-location, but some location can have multiple Ship-Tos :-/
    gsx_accounts = models.ManyToManyField(
        GsxAccount,
        blank=True,
        verbose_name=_('Accounts')
    )

    gsx_shipto = models.CharField(
        max_length=10,
        default='',
        blank=True,
        verbose_name=_('Ship-To')
    )

    gsx_tz = models.CharField(
        max_length=4,
        default='CEST',
        verbose_name=_('Timezone'),
        choices=gsxws.GSX_TIMEZONES
    )

    notes = models.TextField(
        blank=True,
        default='9:00 - 18:00',
        verbose_name=_('Notes'),
        help_text=_('Will be shown on print templates')
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="managed_locations",
        limit_choices_to={'is_visible': True}
    )

    enabled = models.BooleanField(
        default=True,
        verbose_name=_('Enabled')
    )

    checkin = models.BooleanField(
        default=True,
        verbose_name=_('Use for check-in')
    )

    @classmethod
    def get_checkin_list(cls):
        results = []
        for l in cls.objects.filter(checkin=True):
            results.append({'pk': l.pk, 'name': l.title})

        return results

    def get_shipto_choices(self):
        return self.gsx_accounts.values_list('ship_to', 'ship_to')

    def get_country(self):
        try:
            return TIMEZONE_COUNTRY[self.timezone]
        except KeyError:
            return 'FI'

    def ship_to_choices(self):
        choices = []
        for i in self.gsx_accounts.all():
            choices.append((i.ship_to, i.ship_to))
        return choices

    def get_admin_url(self):
        return reverse('admin-edit_location', args=[self.pk])

    def gsx_address(self):
        return {
            'city'          : self.city,
            'zipCode'       : self.zip_code,
            'country'       : self.get_country(),
            'primaryPhone'  : self.phone,
            'emailAddress'  : self.email,
        }

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title',)
        app_label = 'servo'
        get_latest_by = 'id'
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')
        unique_together = ('title', 'site',)


class Configuration(models.Model):
    site = models.ForeignKey(Site, editable=False, default=defaults.site_id)
    key = models.CharField(max_length=255)
    value = models.TextField(default='', blank=True)

    @classmethod
    def true(cls, key):
        return cls.conf(key) == 'True'

    @classmethod
    def false(cls, key):
        return not cls.true(key)

    @classmethod
    def get_company_logo(cls):
        return cls.conf('company_logo')

    @classmethod
    def default_subject(cls):
        return cls.conf('default_subject')

    @classmethod
    def get_default_sender(cls, user):
        """
        Returns the sender address to use for notifications
        """
        conf = cls.conf()
        sender = conf.get('default_sender')

        if sender == 'user':
            return user.email
        if sender == 'location':
            return user.get_location().email

        return conf.get('default_sender_custom')

    @classmethod
    def track_inventory(cls):
        return cls.true('track_inventory')

    @classmethod
    def notify_location(cls):
        return cls.true('notify_location')

    @classmethod
    def notify_email_address(cls):
        """
        Returns the email address to send reports to
        or None if it's invalid
        """
        from django.core.validators import validate_email
        try:
            validate_email(conf['notify_address'])
            return conf['notify_address']
        except Exception:
            pass

    @classmethod
    def autocomplete_repairs(cls):
        return cls.true('autocomplete_repairs')

    @classmethod
    def smtp_ssl(cls):
        return cls.true('smtp_ssl')

    @classmethod
    def get_smtp_server(cls):
        host, port = cls.conf('smtp_host'), 25

        if empty(host):
            raise ConfigurationError('SMTP server not configured')

        if len(host.split(':')) == 2:
            return host.split(':')

        return host, port

    @classmethod
    def get_imap_server(cls):
        import imaplib
        conf = cls.conf()

        if not conf.get('imap_host'):
            raise ValueError("No IMAP server defined - check your configuration")

        if conf.get('imap_ssl'):
            server = imaplib.IMAP4_SSL(conf['imap_host'])
        else:
            server = imaplib.IMAP4(conf['imap_host'])

        server.login(conf['imap_user'], conf['imap_password'])
        server.select()
        return server

    @classmethod
    def conf(cls, key=None):
        """
        Returns the admin-configurable config of the site
        """
        config = cache.get('config')
        if config is None:
            config = dict()
            for r in Configuration.objects.all():
                config[r.key] = r.value

            cache.set('config', config)

        return config.get(key) if key else config

    def save(self, *args, **kwargs):
        config = super(Configuration, self).save(*args, **kwargs)
        # Using cache instead of session since it's shared among
        # all the users of the instance
        cache.set('config', config, 60*60*24*1)

    class Meta:
        app_label = 'servo'
        unique_together = ('key', 'site',)


class Property(models.Model):
    TYPES = (
        ('customer',    _('Customer')),
        ('order',       _('Order')),
        ('product',     _('Product'))
    )

    title = models.CharField(
        max_length=255,
        default=_('New Field'),
        verbose_name=_('title')
    )

    type = models.CharField(
        max_length=32,
        choices=TYPES,
        default=TYPES[0],
        verbose_name=_('type')
    )
    format = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_('format')
    )
    value = models.TextField(blank=True, default='', verbose_name=_('value'))

    def __unicode__(self):
        return self.title

    def get_admin_url(self):
        return reverse('admin-edit_field', args=[self.type, self.pk])

    def values(self):
        if self.value is None:
            return []
        else:
            return self.value.split(', ')

    class Meta:
        app_label = 'servo'
        ordering = ['title']
        verbose_name = _('Field')
        verbose_name_plural = _('Fields')


class Search(models.Model):
    query = models.TextField()
    model = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    shared = models.BooleanField(default=True)

    class Meta:
        app_label = 'servo'


class Notification(models.Model):
    """
    A notification is a user-configurable response to an event
    """
    KINDS = (('ORDER', _('Order')), ('NOTE', _('Note')),)
    ACTIONS = (('created', u'Luotu'), ('edited', u'Muokattu'))

    kind = models.CharField(max_length=16)
    action = models.CharField(max_length=16)
    message = models.TextField()

    class Meta:
        app_label = 'servo'


class Template(models.Model):
    title = models.CharField(
        blank=False,
        unique=True,
        max_length=128,
        verbose_name=_('Title'),
        default=_('New Template')
    )

    content = models.TextField(blank=False, verbose_name=_('Content'))

    @classmethod
    def templates(self):
        choices = Template.objects.all().values_list('title', flat=True)
        return list(choices)

    def render(self, context):
        from django import template
        tpl = template.Template(self.content)
        return tpl.render(template.Context({'order': context}))

    def get_absolute_url(self):
        return reverse('notes-template', args=[self.pk])

    def get_admin_url(self):
        return reverse('admin-edit_template', args=[self.pk])

    def get_delete_url(self):
        return reverse('admin-delete_template', args=[self.pk])

    class Meta:
        ordering = ['title']
        app_label = "servo"
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')


class Attachment(BaseItem):
    """
    A file attached to something
    """
    mime_type = models.CharField(max_length=64, editable=False)
    content = models.FileField(
        upload_to='attachments',
        verbose_name=_('file'),
        validators=[file_upload_validator]
    )

    @classmethod
    def get_content_type(cls, model):
        return ContentType.objects.get(app_label='servo', model=model)

    @classmethod
    def from_file(cls, file):
        """
        Returns an attachment object from the file data
        """
        attachment = cls(content=file)
        attachment.save()

    def save(self, *args, **kwargs):
        DENIED_EXTENSIONS = ('.htm', '.html', '.py', '.js',)
        filename = self.content.name.lower()
        ext = os.path.splitext(filename)[1]

        if ext in DENIED_EXTENSIONS:
            raise ValueError(_(u'%s is not of an allowed file type') % filename)

        return super(Attachment, self).save(*args, **kwargs)

    def __unicode__(self):
        return os.path.basename(self.content.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def from_url(self, url):
        pass

    def get_absolute_url(self):
        return reverse("files-view_file", args=[self.pk])

    class Meta:
        app_label = "servo"
        get_latest_by = "id"


@receiver(post_save, sender=Attachment)
def set_mimetype(sender, instance, created, **kwargs):
    if created:
        import subprocess
        path = instance.content.path
        mimetype = subprocess.check_output(['file', '-b', '--mime-type', path]).strip()
        instance.mime_type = mimetype
        instance.save()
