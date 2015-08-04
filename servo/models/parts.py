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

import yaml
import gsxws

from django.db import models
from django.utils import timezone
from django.core.files import File
from django.utils.translation import ugettext_lazy as _

from servo.models.shipments import Shipment
from servo.models.order import ServiceOrderItem
from servo.models.purchases import PurchaseOrder, PurchaseOrderItem


def symptom_modifiers():
    return gsxws.MODIFIERS


def symptom_codes(group):
    """
    Return symptom codes for component group
    """
    if group == '':
        return

    data = yaml.load(open("servo/fixtures/comptia.yaml", "r"))
    symptoms = data[group]['symptoms']
    srted = sorted(symptoms)
    codes = [(k, "%s - %s " % (k, symptoms[k])) for k in srted]
    return codes


class ServicePart(models.Model):
    """
    Stores the data necessary to connect our ServiceOrderItems
    with the corresponding GSX parts
    """
    repair = models.ForeignKey("Repair", editable=False)
    order_item = models.ForeignKey(ServiceOrderItem, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, null=True, editable=False)

    comptia_code = models.CharField(
        max_length=4,
        editable=False,
        verbose_name=_("Symptom Code")
    )
    comptia_modifier = models.CharField(
        max_length=1,
        editable=False,
        verbose_name=_("Symptom Modifier")
    )

    # maps to partsInfo/orderLineNumber
    line_number = models.SmallIntegerField(null=True, editable=False)
    registered_for_return = models.BooleanField(default=False)
    returned_at = models.DateTimeField(null=True, editable=False)

    ship_to = models.CharField(max_length=18, editable=False)
    part_title = models.CharField(max_length=128)
    part_number = models.CharField(max_length=18)
    service_order = models.CharField(max_length=10)
    return_order = models.CharField(max_length=10, default='')

    # maps Return Status (Known Bad Board)
    return_status = models.CharField(default='', max_length=128, editable=False)
    # maps Return Code (KBB, NRET)
    return_code = models.CharField(default='', max_length=4, editable=False)
    # maps to GSX Order Status
    order_status = models.CharField(default='', max_length=128, editable=False)
    # maps to GSX Order Status Code
    order_status_code = models.CharField(default='', max_length=4, editable=False)

    COVERAGE_STATUS_CHOICES = (
        ('CC', _('Custom Bid Contracts')),
        ('CS', _('Customer Satisfaction')),
        ('DO', _('DOA Coverage')),
        ('LI', _('Apple Limited Warranty')),
        ('MU', _('Missing Upon First Use')),
        ('OO', _('Out of Warranty (No Coverage)')),
        ('PA', _('AppleCare Parts Agreement')),
        ('PP', _('AppleCare Protection Plan')),
        ('QP', _('Quality Program')),
        ('RA', _('AppleCare Repair Agreement')),
        ('RE', _('Repeat Service')),
        ('PT', _('Additional Part Coverage')),
        ('EC', _('Additional Service Coverage')),
        ('C1', _('NEW - AppleCare Protection Plan')),
        ('VW', _('Consumer Law Coverage')),
    )
    """
    coverage_status = models.CharField(
        default='',
        max_length=3,
        choices=COVERAGE_STATUS_CHOICES
    )
    """
    coverage_description = models.CharField(
        default='',
        max_length=128,
        editable=False
    )
    
    shipment = models.ForeignKey(Shipment, null=True)
    box_number = models.PositiveIntegerField(null=True)
    return_label = models.FileField(
        null=True,
        editable=False,
        upload_to="return_labels"
    )
    carrier_url = models.CharField(default='', max_length=255, editable=False)

    def get_symptom_code_display(self):
        codes = self.get_comptia_symptoms() or []
        try:
            return [c[1] for c in codes if c[0] == self.comptia_code][0]
        except IndexError:
            return self.comptia_code

    def get_symptom_modifier_display(self):
        mods = symptom_modifiers()
        try:
            return [m[1] for m in mods if m[0] == self.comptia_modifier][0]
        except IndexError:
            return self.comptia_modifier

    @property
    def reference(self):
        return self.repair.reference

    @classmethod
    def from_soi(cls, repair, soi):
        """
        Creates and returns a ServicePart from a repair and ServiceOrderItem
        """
        part = cls(repair=repair, order_item=soi)
        part.part_title = soi.title
        part.part_number = soi.code
        part.service_order = soi.order.code
        part.ship_to = repair.gsx_account.ship_to
        part.comptia_code = soi.comptia_code
        part.comptia_modifier = soi.comptia_modifier
        return part

    def order(self, user, po=None):
        """
        Purchase this Service Part
        """
        if po is None:
            po = PurchaseOrder()
            po.location = user.get_location()
            po.sales_order = self.repair.order
            po.reference = self.repair.reference
            po.confirmation = self.repair.confirmation
            po.created_by = user
            po.supplier = "Apple"
            po.save()

        self.purchase_order = po
        poi = PurchaseOrderItem(purchase_order=po)
        poi.code = self.part_number
        poi.title = self.part_title
        poi.order_item = self.order_item
        poi.product = self.order_item.product
        poi.price = self.order_item.get_purchase_price()

        poi.save()

        if po.submitted_at is None:
            po.submit(user)

        self.save()

    def is_replacement(self):
        return self.order_item.product.part_type == 'REPLACEMENT'

    def mark_doa(self):
        """
        Marking a part DOA means we get a new part, so:
        - make a copy of the old part
        """
        # Update our PO so we know to expect the replacement for the DOA part
        poi = PurchaseOrderItem(price=0, purchase_order=self.purchase_order)
        poi.product = self.order_item.product
        poi.order_item = self.order_item
        poi.ordered_at = timezone.now()
        poi.save()

        # Create a copy of this part and reset
        new_part                = self
        new_part.pk             = None
        new_part.shipment       = None
        new_part.line_number    = None
        new_part.returned_at    = None

        new_part.return_order   = ''
        new_part.order_status   = ''
        new_part.return_label   = None
        new_part.order_status_code = ''
        new_part.coverage_description = ''
        new_part.registered_for_return = False

        new_part.save()

    def set_part_details(self, gsx_part):
        """
        Updates this part to match the info from gsx_part
        """
        self.comptia_code = gsx_part.comptiaCode or ''
        self.return_order = gsx_part.returnOrderNumber or ''
        self.comptia_modifier = gsx_part.comptiaModifier or ''

        self.order_status = gsx_part.orderStatus or ''
        self.order_status_code = gsx_part.orderStatusCode or ''
        self.coverage_description = gsx_part.partCoverageDescription or ''

        self.return_code = gsx_part.returnCode or ''
        self.return_status = gsx_part.returnStatus or ''
        self.carrier_url = gsx_part.carrierURL or ''
        self.line_number = gsx_part.orderLineNumber

        return self

    def update_part(self, return_data, return_type, user):
        """
        gsx/returns/Parts Return Update
        """
        self.repair.connect_gsx(user)

        p = {'partNumber': self.part_number, 'returnType': return_type}
        p.update(return_data)
        part = gsxws.RepairOrderLine(**p)
        ret = gsxws.Return()

        ret.update_parts(self.repair.confirmation, [part])

        if return_type == Shipment.RETURN_DOA:
            self.mark_doa()

    def can_return(self):
        return not self.return_order == ''

    def get_return_title(self):
        if self.registered_for_return:
            return _("Unregister from Return")

        return _("Register for Return")

    def register_for_return(self, user):
        """
        Registers this part for the current bulk return
        """
        location = user.get_location()
        ship_to = self.repair.gsx_account.ship_to
        shipment = Shipment.get_current(user, location, ship_to)
        shipment.toggle_part(self)

    def to_gsx(self):
        """
        Returns a GSX ServicePart entry for this part
        """
        part = gsxws.ServicePart(self.part_number)
        part.returnOrderNumber = self.return_order
        if self.box_number > 0:
            part.boxNumber = self.box_number
        return part

    def needs_comptia_code(self):
        """
        CompTIA not required for Replacement and Other category parts.
        In practice this is here for Adjustment-type parts (#011-0663)
        """
        return self.order_item.product.part_type != 'ADJUSTMENT'

    def get_repair_order_line(self):
        """
        Returns GSX RepairOrderLine entry for this part
        """
        ol = gsxws.RepairOrderLine()
        ol.partNumber = self.part_number

        oi = self.order_item
        ol.abused = oi.is_abused

        if self.needs_comptia_code():
            ol.comptiaCode = self.comptia_code
            ol.comptiaModifier = self.comptia_modifier

        device = self.repair.device

        # Warranty only when warranty price (0) and no damage
        # warranty means outOfWarrantyFlag=False
        if device and not oi.is_abused:
            if device.has_warranty:
                ol.returnableDamage = not oi.is_warranty

        return ol

    def get_comptia_symptoms(self):
        """
        Returns the appropriate CompTIA codes for this part
        """
        product = self.order_item.product
        return symptom_codes(product.component_code)

    def get_return_label(self):
        """
        Returns the GSX return label for this part
        """
        if self.return_label.name == "":
            # Return label not yet set, get it...
            label = gsxws.Return(self.return_order).get_label(self.part_number)
            filename = "%s_%s.pdf" % (self.return_order, self.part_number)

            f = File(open(label.returnLabelFileData))
            self.return_label = f
            self.save()
            self.return_label.save(filename, f)

        return self.return_label.read()

    def update_module_sn(self):
        """
        Updates the GSX module serial numbers
        """
        part = gsxws.ServicePart(self.order_item.code)
        part.oldSerialNumber = self.order_item.kbb_sn
        part.serialNumber = self.order_item.sn
        part.reasonCode = "OT"
        part.isPartDOA = "N"
        repair = self.repair.get_gsx_repair()
        return repair.update_sn([part])

    def update_replacement_sn(self):
        """
        Updates the Whole-Unit swap KGB SN
        With the user's own GSX credentials, falling back to the defaults
        """
        repair = self.repair.get_gsx_repair()
        return repair.update_kgb_sn(self.order_item.sn)

    def can_update_sn(self):
        soi = self.order_item
        return not soi.sn == ''

    def update_sn(self):
        # CTS parts not eligible for SN update
        if self.return_status == 'Convert To Stock':
            return

        if not self.repair.confirmation:
            raise ValueError(_('GSX repair has no dispatch ID'))

        product = self.order_item.product

        if not product.is_serialized:
            return

        if product.part_type == "MODULE":
            self.update_module_sn()
        elif product.part_type == "REPLACEMENT":
            self.update_replacement_sn()

    def lookup(self):
        return gsxws.Part(partNumber=self.part_number).lookup()

    def save(self, *args, **kwargs):
        if self.comptia_code is None:
            oi = self.order_item
            self.comptia_code = oi.comptia_code
            self.comptia_modifier = oi.comptia_modifier

        super(ServicePart, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'ServicePart %s' % self.part_number

    class Meta:
        app_label = "servo"
        get_latest_by = "id"
        ordering = ("order_item",)
        # A part can only appear once per shipment
        unique_together = ("id", "shipment",)
