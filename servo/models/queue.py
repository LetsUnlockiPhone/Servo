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

from datetime import timedelta
from django.conf import settings

from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from servo import defaults
from servo.models.common import Location


class Queue(models.Model):
    site = models.ForeignKey(
        Site,
        editable=False,
        default=defaults.site_id
    )

    title = models.CharField(
        max_length=255,
        unique=True,
        default=_('New Queue'),
        verbose_name=_('Title')
    )

    keywords = models.TextField(
        default='',
        blank=True,
        help_text=_('Orders with devices matching these keywords will be automatically assigned to this queue')
    )

    locations = models.ManyToManyField(
        Location,
        verbose_name=_('locations'),
        help_text=_("Pick the locations you want this queue to appear in.")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_('description')
    )

    PRIO_LOW    = 0
    PRIO_NORMAL = 1
    PRIO_HIGH   = 2

    PRIORITIES = (
        (PRIO_HIGH, _("High")),
        (PRIO_NORMAL, _("Normal")),
        (PRIO_LOW, _("Low"))
    )

    priority = models.IntegerField(
        default=PRIO_NORMAL,
        choices=PRIORITIES,
        verbose_name=_("priority")
    )

    status_created = models.ForeignKey(
        'QueueStatus',
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_(u'Order Created'),
        help_text=_("Order has ben placed to a queue")
    )

    status_assigned = models.ForeignKey(
        'QueueStatus',
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_(u'Order Assigned'),
        help_text=_("Order has ben assigned to a user")
    )

    status_products_ordered = models.ForeignKey(
        'QueueStatus',
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_("Products Ordered"),
        help_text=_("Purchase Order for this Service Order has been submitted")
    )
    status_products_received = models.ForeignKey(
        'QueueStatus',
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_("Products Received"),
        help_text=_("Products have been received")
    )
    status_repair_completed = models.ForeignKey(
        'QueueStatus',
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_("Repair Completed"),
        help_text=_("GSX repair completed")
    )

    status_dispatched = models.ForeignKey(
        'QueueStatus',
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_("Order Dispatched")
    )

    status_closed = models.ForeignKey(
        'QueueStatus',
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_("Order Closed")
    )

    gsx_soldto = models.CharField(
        blank=True,
        default='',
        max_length=10,
        verbose_name=_("Sold-To"),
        help_text=_("GSX queries of an order in this queue will be made using this Sold-To")
    )

    order_template = models.FileField(
        null=True,
        blank=True,
        upload_to="templates",
        verbose_name=_("order template"),
        help_text=_("HTML template for Service Order/Work Confirmation")
    )
    quote_template = models.FileField(
        null=True,
        blank=True,
        upload_to="templates",
        verbose_name=_("quote template"),
        help_text=_("HTML template for cost estimate")
    )
    receipt_template = models.FileField(
        null=True,
        blank=True,
        upload_to="templates",
        verbose_name=_("receipt template"),
        help_text=_("HTML template for Sales Order Receipt")
    )
    dispatch_template = models.FileField(
        null=True,
        blank=True,
        upload_to="templates",
        verbose_name=_("dispatch template"),
        help_text=_("HTML template for dispatched order")
    )

    def get_admin_url(self):
        return reverse('admin-edit_queue', args=[self.pk])

    def get_order_count(self, max_state=2):
        count = self.order_set.filter(state__lt=max_state).count()
        return count if count > 0 else ''

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']
        app_label = "servo"
        verbose_name = _("Queue")
        verbose_name_plural = _("Queues")
        unique_together = ('title', 'site',)


class Status(models.Model):
    site = models.ForeignKey(
        Site,
        editable=False,
        default=defaults.site_id
    )

    FACTOR_CHOICES = (
        (60,        _('Minutes')),
        (3600,      _('Hours')),
        (86400,     _('Days')),
        (604800,    _('Weeks')),
        (2419200,   _('Months')),
    )

    title = models.CharField(
        max_length=255,
        default=_(u'New Status'),
        verbose_name=_(u'name')
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_(u'description')
    )
    limit_green = models.IntegerField(
        default=1,
        verbose_name=_(u'green limit')
    )
    limit_yellow = models.IntegerField(
        default=15,
        verbose_name=_(u'yellow limit')
    )
    limit_factor = models.IntegerField(
        choices=FACTOR_CHOICES,
        default=FACTOR_CHOICES[0],
        verbose_name=_(u'time unit')
    )
    queue = models.ManyToManyField(
        Queue,
        editable=False,
        through='QueueStatus'
    )

    def is_enabled(self, queue):
        return self in queue.queuestatus_set.all()

    def get_admin_url(self):
        return reverse('admin-edit_status', args=[self.pk])

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'servo'
        ordering = ('title',)
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')
        unique_together = ('title', 'site',)


class QueueStatus(models.Model):
    """
    A status bound to a queue.
    This allows us to set time limits for each status per indiviudal queue
    """
    queue  = models.ForeignKey(Queue)
    status = models.ForeignKey(Status)

    limit_green = models.IntegerField(default=1, verbose_name=_(u'green limit'))
    limit_yellow = models.IntegerField(default=15, verbose_name=_(u'yellow limit'))
    limit_factor = models.IntegerField(
        choices=Status.FACTOR_CHOICES,
        verbose_name=_(u'time unit'),
        default=Status.FACTOR_CHOICES[0][0]
    )

    def get_green_limit(self):
        """
        Gets the green time limit for this QS
        """
        return timezone.now() + timedelta(seconds=self.limit_green*self.limit_factor)

    def get_yellow_limit(self):
        return timezone.now() + timedelta(seconds=self.limit_yellow*self.limit_factor)

    def __unicode__(self):
        return self.status.title

    class Meta:
        app_label = 'servo'
        # A status should only be defined once per queue
        unique_together = ('queue', 'status',)
