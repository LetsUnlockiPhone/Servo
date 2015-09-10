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

import locale

from django.db import models
from django.conf import settings

from pytz import common_timezones
from django.core.cache import cache
from django.core.urlresolvers import reverse
from rest_framework.authtoken.models import Token

from mptt.fields import TreeForeignKey
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, UserManager

from servo import defaults
from servo.models.common import Location, Configuration
from servo.models.queue import Queue
from servo.models.customer import Customer


class ActiveManager(UserManager):
    def get_queryset(self):
        r = super(ActiveManager, self).get_queryset().filter(is_visible=True)
        return r.filter(is_active=True)


class TechieManager(UserManager):
    def get_queryset(self):
        return super(TechieManager, self).get_queryset().filter(tech_id__regex=r'\w{8}')

    def active(self):
        return self.get_queryset().filter(is_active=True)


class User(AbstractUser):

    customer = TreeForeignKey(
        Customer,
        null=True,
        blank=True,
        limit_choices_to={'is_company': True}
    )

    full_name = models.CharField(
        max_length=128,
        editable=False,
        default=_('New User')
    )

    locations = models.ManyToManyField(Location, blank=True)

    #  The location this user is currently in
    location = models.ForeignKey(
        Location,
        null=True,
        related_name='+',
        on_delete=models.PROTECT,
        verbose_name=_('Current Location'),
        help_text=_(u'Orders you create will be registered to this location.')
    )
    queues = models.ManyToManyField(Queue, blank=True, verbose_name=_('queues'))
    LOCALES = (
        ('da_DK.UTF-8', _("Danish")),
        ('nl_NL.UTF-8', _("Dutch")),
        ('en_US.UTF-8', _("English")),
        ('et_EE.UTF-8', _("Estonian")),
        ('fi_FI.UTF-8', _("Finnish")),
        ('sv_SE.UTF-8', _("Swedish")),
    )
    locale = models.CharField(
        max_length=32,
        choices=LOCALES,
        default=LOCALES[0][0],
        verbose_name=_('language'),
        help_text=_("Select which language you want to use Servo in.")
    )

    TIMEZONES = tuple((t, t) for t in common_timezones)
    timezone = models.CharField(
        max_length=128,
        choices=TIMEZONES,
        default=settings.TIMEZONE,
        verbose_name=_('Time zone'),
        help_text=_("Your current timezone")
    )

    REGIONS = (
        ('da_DK.UTF-8', _("Denmark")),
        ('et_EE.UTF-8', _("Estonia")),
        ('fi_FI.UTF-8', _("Finland")),
        ('en_US.UTF-8', _("United States")),
        ('nl_NL.UTF-8', _("Netherlands")),
        ('sv_SE.UTF-8', _("Sweden")),
    )
    region = models.CharField(
        max_length=32,
        choices=REGIONS,
        default=defaults.locale,
        verbose_name=_('region'),
        help_text=_("Affects formatting of numbers, dates and currencies.")
    )
    should_notify = models.BooleanField(
        default=True,
        verbose_name=_('Enable notifications'),
        help_text=_("Enable notifications in the toolbar.")
    )
    notify_by_email = models.BooleanField(
        default=False,
        verbose_name=_('email notifications'),
        help_text=_("Event notifications will also be emailed to you.")
    )
    autoprint = models.BooleanField(
        default=True,
        verbose_name=_('print automatically'),
        help_text=_("Opens print dialog automatically.")
    )
    tech_id = models.CharField(
        blank=True,
        default='',
        max_length=16,
        verbose_name=_("tech ID")
    )
    gsx_userid = models.CharField(
        blank=True,
        default='',
        max_length=128,
        verbose_name=_("User ID")
    )

    gsx_poprefix = models.CharField(
        blank=True,
        default='',
        max_length=8,
        verbose_name=_("PO prefix"),
        help_text=_("GSX repairs you create will be prefixed")
    )

    photo = models.ImageField(
        null=True,
        blank=True,
        upload_to="avatars",
        verbose_name=_('photo'),
        help_text=_("Maximum avatar size is 1MB")
    )

    is_visible = models.BooleanField(default=True, editable=False)

    objects = UserManager()
    techies = TechieManager()
    active  = ActiveManager()

    def get_location_list(self):
        results = []
        for l in self.locations.all():
            results.append({'pk': l.pk, 'name': l.title})

        return results

    @classmethod
    def serialize(cls, queryset):
        results = []
        for u in queryset:
            results.append({'pk': u.pk, 'name': u.get_name()})

        return results

    @classmethod
    def refresh_nomail(cls):
        users = cls.active.filter(notify_by_email=False)
        nomail = [u.email for u in users]
        cache.set('nomail', nomail)

    @classmethod
    def get_checkin_group(cls):
        """
        Returns all the active members of the check-in group
        """
        group = Configuration.conf('checkin_group')
        return cls.active.filter(groups__pk=group)

    @classmethod
    def get_checkin_group_list(cls):
        return cls.serialize(cls.get_checkin_group())

    @classmethod
    def get_checkin_user(cls):
        return cls.objects.get(pk=Configuration.conf('checkin_user'))

    def create_token(self):
        token = Token.objects.create(user=self)
        return token.key

    def delete_tokens(self):
        self.get_tokens().delete()

    def get_tokens(self):
        return Token.objects.filter(user=self)

    def notify(self, msg):
        pass

    def get_group(self):
        """
        Returns the user's primary (first) group
        """
        return self.groups.first()

    def get_icon(self):
        return 'icon-star' if self.is_staff else 'icon-user'

    def get_name(self):
        return self.full_name if len(self.full_name) > 1 else self.username

    def get_location(self):
        return self.location

    def get_unread_message_count(self):
        key = '%s_unread_message_count' % self.user.email
        count = cache.get(key, 0)
        return count if count > 0 else ""

    def get_order_count(self, max_state=2):
        count = self.order_set.filter(state__lt=max_state).count()
        return count if count > 0 else ""

    def order_count_in_queue(self, queue):
        count = self.user.order_set.filter(queue=queue).count()
        return count if count > 0 else ""

    def save(self, *args, **kwargs):
        self.full_name = u"{0} {1}".format(self.first_name, self.last_name)
        users = User.objects.filter(notify_by_email=False)
        nomail = [u.email for u in users]
        cache.set('nomail', nomail)
        return super(User, self).save(*args, **kwargs)

    def activate_locale(self):
        """
        Activates this user's locale
        """
        try:
            lc = self.locale.split('.')
            region = self.region.split('.')
            locale.setlocale(locale.LC_TIME, region)
            locale.setlocale(locale.LC_MESSAGES, lc)
            locale.setlocale(locale.LC_NUMERIC, region)
            locale.setlocale(locale.LC_MONETARY, region)
        except Exception as e:
            locale.setlocale(locale.LC_ALL, None)

        # Return the language code
        return self.locale.split('_', 1)[0]

    def get_avatar(self):
        try:
            return self.photo.url
        except ValueError:
            return "/static/images/avatar.png"

    def get_admin_url(self):
        return reverse('admin-edit_user', args=[self.pk])

    def __unicode__(self):
        return self.get_name() or self.username

    class Meta:
        app_label = "servo"
        ordering = ("full_name",)
        verbose_name = _('User')
        verbose_name_plural = _('Users & Groups')


class UserGroup(Group):

    def members_as_list(self):
        pass

    def get_name(self):
        return self.name

    def get_admin_url(self):
        return reverse('admin-edit_group', args=[self.pk])

    class Meta:
        app_label = 'servo'
