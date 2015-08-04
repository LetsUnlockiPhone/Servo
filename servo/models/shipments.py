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

import gsxws

from django.db import models

from django.conf import settings
from django.utils import timezone
from django.core.files import File
from django.utils.translation import ugettext_lazy as _

from servo.models import Location


class Shipment(models.Model):
    """
    Bulk returns
    """
    RETURN_DOA = 1 # Dead On Arrival
    RETURN_GPR = 2 # Good Part Return
    RETURN_CTS = 3 # Convert to stock

    location = models.ForeignKey(Location, editable=False)

    ship_to = models.CharField(
        default='',
        max_length=10,
        editable=False,
    )

    return_id = models.CharField(
        null=True,
        unique=True,
        max_length=10,
        editable=False,
        help_text="The return ID returned by GSX"
    )

    tracking_id = models.CharField(
        blank=True,
        default='',
        max_length=30,
        verbose_name=_('Tracking ID'),
        help_text="Carrier's tracking ID"
    )

    tracking_url = models.URLField(
        null=True,
        editable=False,
        help_text="The tracking URL returned by GSX"
    )

    packing_list = models.FileField(
        null=True,
        editable=False,
        upload_to='returns',
        help_text="The PDF returned by GSX"
    )

    carrier = models.CharField(
        blank=True,
        default='',
        max_length=18,
        choices=gsxws.CARRIERS,
        verbose_name=_('carrier')
    )

    created_at = models.DateTimeField(auto_now=True, editable=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="created_shipments"
    )

    dispatched_at = models.DateTimeField(null=True, editable=False)

    dispatched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        editable=False,
        related_name='dispatched_shipments'
    )

    width = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('width')
    )

    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('height')
    )

    length = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('length')
    )

    weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('weight')
    )

    @classmethod
    def get_current(cls, user, location, ship_to):
        try:
            shipment = cls.objects.get(dispatched_at=None,
                                       location=location,
                                       ship_to=ship_to)
        except cls.DoesNotExist:
            shipment = cls.objects.create(created_by=user,
                                          location=location,
                                          ship_to=ship_to)

        return shipment

    def toggle_part(self, part):
        part.registered_for_return = not part.registered_for_return
        part.save()

        if part.registered_for_return:
            self.servicepart_set.add(part)
        else:
            self.servicepart_set.remove(part)

    def verify(self):
        """
        Verifies this shipment with GSX
        """
        pass

    def register_bulk_return(self, user):
        """
        Registers bulk return with GSX
        """
        parts = []  # Array of outbound parts in GSX format

        gsx_act = self.location.gsx_accounts.get(ship_to=self.ship_to)
        gsx_act.connect(user)

        for p in self.servicepart_set.all().order_by('box_number'):
            parts.append(p.to_gsx())

        ret = gsxws.Return(shipToCode=self.ship_to)

        ret.notes = ""
        ret.width = self.width
        ret.length = self.length
        ret.height = self.height
        ret.carrierCode = self.carrier
        ret.trackingNumber = self.tracking_id
        ret.estimatedTotalWeight = self.weight

        result = ret.register_parts(parts)
        ret.bulkReturnOrder = parts
        self.dispatched_by = user
        self.dispatched_at = timezone.now()
        self.return_id = result.bulkReturnId
        self.tracking_url = result.trackingURL

        self.save()

        filename = "bulk_return_%s.pdf" % self.return_id
        self.packing_list.save(filename, File(open(result.packingList)))

    def get_absolute_url(self):
        return "/products/shipments/returns/%d/" % self.pk

    def save(self, *args, **kwargs):
        if not self.pk:
            self.location = self.created_by.location

        super(Shipment, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'Shipment #%s from %s' % (self.pk, self.location.title)

    class Meta:
        app_label = "servo"
        get_latest_by = 'id'
        ordering = ('-dispatched_at',)
