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

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.dispatch import receiver
from django.db.models.signals import post_save

from servo import defaults
from servo.models.common import Location, Configuration
from servo.models.product import Product, Inventory
from servo.models.order import Order, AbstractOrderItem, ServiceOrderItem


class PurchaseOrder(models.Model):
    """
    A purchase order(PO) consists of different purchase order items
    all of which may reference individual Service Orders.
    When a PO is submitted, the included items are registered
    to the /products/incoming/ list (items that have not yet arrived).
    A PO cannot be edited after it's been submitted.

    Creating a PO from an SO only creates the PO, it does not submit it.
    """
    location = models.ForeignKey(
        Location,
        editable=False,
        help_text=_('The location from which this PO was created')
    )
    sales_order = models.ForeignKey(Order, null=True, editable=False)
    reference = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_("reference"),
    )
    confirmation = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_("confirmation"),
    )

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    submitted_at = models.DateTimeField(null=True, editable=False)

    supplier = models.CharField(
        blank=True,
        max_length=32,
        verbose_name=_("supplier")
    )
    carrier = models.CharField(
        blank=True,
        max_length=32,
        verbose_name=_("carrier")
    )
    tracking_id = models.CharField(
        blank=True,
        max_length=128,
        verbose_name=_("tracking ID")
    )
    days_delivered = models.IntegerField(
        blank=True,
        default=1,
        verbose_name=_("delivery Time")
    )

    has_arrived = models.BooleanField(default=False)
    total = models.FloatField(null=True, editable=False)
    invoice_id = models.CharField(default='', max_length=10, editable=False)
    invoice = models.FileField(
        null=True,
        editable=False,
        upload_to="gsx_invoices",
        help_text="Apple's sales invoice for this PO"
    )

    def only_apple_parts(self):
        for p in self.purchaseorderitem_set.all():
            if not p.product.is_apple_part:
                return False
        return True

    @property
    def is_editable(self):
        return self.submitted_at is None

    def can_create_gsx_stock(self):
        return self.is_editable and self.confirmation == ''

    def order_items(self, items):
        pass

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        if self.submitted_at:
            return reverse("purchases-view_po", args=[self.pk])
        return reverse("purchases-edit_po", args=[self.pk])

    def sum(self):
        total = 0
        for p in self.purchaseorderitem_set.all():
            total += float(p.price*p.amount)

        return total

    def amount(self):
        amount = 0
        for p in self.purchaseorderitem_set.all():
            amount += p.amount

        return amount

    def submit(self, user):
        "Submits this Purchase Order"
        if self.submitted_at is not None:
            raise ValueError(_("Purchase Order %d has already been submitted") % self.pk)

        location = user.get_location()

        for i in self.purchaseorderitem_set.all():
            inventory = Inventory.objects.get_or_create(location=location,
                                                        product=i.product)[0]
            inventory.amount_ordered += i.amount
            inventory.save()
            i.ordered_at = timezone.now()
            i.save()

        self.submitted_at = timezone.now()
        self.save()

    def cancel(self):
        """
        Cancels this Purchase Order
        Declined Repairs etc
        """
        location = self.created_by.get_location()

        for i in self.purchaseorderitem_set.all():
            inventory = Inventory.objects.get(location=location, product=i.product)
            inventory.amount_ordered -= i.amount
            inventory.save()
            i.expected_ship_date = None
            i.save()

    def add_product(self, product, amount, user):
        """
        Adds a product to this Purchase Order
        """
        poi = PurchaseOrderItem(amount=amount, purchase_order=self)
        poi.created_by = user
        # adding from a Service Order
        if isinstance(product, AbstractOrderItem):
            poi.code = product.product.code
            poi.order_item = product
            poi.price = product.price
            poi.product_id = product.product.id
            poi.title = product.product.title
        # adding from Stock
        if isinstance(product, Product):
            poi.code = product.code
            poi.title = product.title
            poi.product_id = product.id
            poi.price = product.price_purchase_stock

        poi.save()

    def delete(self, *args, **kwargs):
        if self.submitted_at:
            raise ValueError(_('Submitted orders cannot be deleted'))
        return super(PurchaseOrder, self).delete(*args, **kwargs)

    class Meta:
        ordering = ('-id',)
        app_label = 'servo'


class PurchaseOrderItem(AbstractOrderItem):
    "An item being purchased"
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Purchase Price"),
        help_text=_("Purchase price without taxes")
    )

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        editable=False,
        verbose_name=_("Purchase Order")
    )

    order_item = models.ForeignKey(ServiceOrderItem, null=True, editable=False)
    reference = models.CharField(default='', blank=True, max_length=128)
    ordered_at = models.DateTimeField(null=True, editable=False)

    expected_ship_date = models.DateField(null=True, editable=False)
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("arrived")
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        editable=False,
        related_name='+'
    )

    @classmethod
    def from_soi(cls, po, soi, user):
        """
        Creates a new POI from a Sales Order item
        """
        poi = cls(purchase_order=po, order_item=soi)
        poi.code = soi.code
        poi.title = soi.title
        poi.created_by = user

        poi.price = soi.get_purchase_price()
        poi.product = soi.product

        return poi

    def get_incoming_url(self):
        """
        Returns the correct URL to receive this item
        """
        if self.received_at is None:
            date = "0000-00-00"
        else:
            date = self.received_at.strftime("%Y-%m-%d")

        return "/sales/shipments/incoming/%s/%d/" % (date, self.pk)

    def receive(self, user):
        if self.received_at is not None:
            raise ValueError(_("Product has already been received"))
        self.received_at = timezone.now()
        self.received_by = user
        self.save()

    def save(self, *args, **kwargs):
        super(PurchaseOrderItem, self).save(*args, **kwargs)
        # Sync SOI and POI serial numbers
        if self.order_item:
            if self.order_item.sn and not self.sn:
                self.sn = self.order_item.sn
            else:
                self.order_item.sn = self.sn

            self.order_item.save()

    class Meta:
        ordering = ('id',)
        app_label = 'servo'
        get_latest_by = 'id'


@receiver(post_save, sender=PurchaseOrderItem)
def trigger_product_received(sender, instance, created, **kwargs):

    if instance.received_at is None:
        return

    product = instance.product
    po = instance.purchase_order
    location = po.created_by.get_location()

    inventory = Inventory.objects.get_or_create(location=location, product=product)[0]

    # Receiving an incoming item
    if Configuration.track_inventory():
        try:
            inventory.amount_ordered -= instance.amount
            inventory.amount_stocked += instance.amount
            inventory.save()
        except Exception:
            ref = po.reference or po.confirmation
            ed = {'prod': product.code, 'ref': ref}
            raise ValueError(_('Cannot receive item %(prod)s (%(ref)s)') % ed)

    sales_order = instance.purchase_order.sales_order

    if sales_order is None:
        return

    # Trigger status change for parts receive
    if sales_order.queue:
        new_status = sales_order.queue.status_products_received
        if new_status and sales_order.is_editable:
            user = instance.received_by or instance.created_by
            sales_order.set_status(new_status, user)


@receiver(post_save, sender=PurchaseOrder)
def trigger_purchase_order_created(sender, instance, created, **kwargs):

    sales_order = instance.sales_order

    if sales_order is None:
        return

    if not sales_order.is_editable:
        return

    if created:
        msg = _("Purchase Order %d created") % instance.id
        sales_order.notify("po_created", msg, instance.created_by)

    # Trigger status change for GSX repair submit (if defined)
    if instance.submitted_at:
        if sales_order.queue:
            queue = sales_order.queue
            if queue.status_products_ordered:
                # Queue has a status for product_ordered - trigger it
                new_status = queue.status_products_ordered
                sales_order.set_status(new_status, instance.created_by)
