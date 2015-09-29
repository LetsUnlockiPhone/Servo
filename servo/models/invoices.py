# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.dispatch import receiver
from django.db.models.signals import post_save

from servo.models import (User, Customer, Order, Location, 
                          AbstractOrderItem, ServiceOrderItem,)


class Invoice(models.Model):
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)

    PAYMENT_METHODS = (
        (0, _("No Charge")),
        (1, _("Cash")),
        (2, _("Invoice")),
        (3, _("Credit Card")),
        (4, _("Mail payment")),
        (5, _("Online payment"))
    )

    payment_method = models.IntegerField(
        editable=False,
        choices=PAYMENT_METHODS,
        default=PAYMENT_METHODS[0][0],
        verbose_name=_("Payment Method")
    )

    is_paid  = models.BooleanField(default=False, verbose_name=_("Paid"))
    paid_at  = models.DateTimeField(null=True, editable=False)
    order    = models.ForeignKey(Order, editable=False)
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        editable=False
    )
    customer = models.ForeignKey(
        Customer,
        null=True,
        editable=False,
        on_delete=models.SET_NULL
    )

    # We remember the following so that the customer info on the invoice 
    # doesn't change if the customer is modified or deleted
    customer_name = models.CharField(
        max_length=255,
        default=_("Walk-in"),
        verbose_name=_("Name")
    )
    customer_phone = models.CharField(
        null=True,
        blank=True,
        max_length=128,
        verbose_name=_("Phone")
    )
    customer_email = models.CharField(
        null=True,
        blank=True,
        max_length=128,
        verbose_name=_("Email")
    )
    customer_address = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_("Address")
    )
    reference = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_("Reference")
    )

    total_net   = models.DecimalField(max_digits=8, decimal_places=2) # total w/o taxes
    total_tax   = models.DecimalField(max_digits=8, decimal_places=2) # total taxes
    total_gross = models.DecimalField(max_digits=8, decimal_places=2) # total with taxes

    total_margin = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        editable=False
    )

    def get_payment_total(self):
        from django.db.models import Sum
        result = self.payment_set.all().aggregate(Sum('amount'))
        return result['amount__sum']

    def get_payment_methods(self):
        """
        Returns the different payment methods used in this invoice
        """
        payments = self.payment_set.all()
        return [x.get_method_display() for x in payments]

    def dispatch(self, products):
        """
        Dispatches the products in this invoice from the inventory
        """
        for p in products:
            soi = ServiceOrderItem.objects.get(pk=p)
            InvoiceItem.from_soi(soi, self)

            soi.product.sell(soi.amount, self.location)
            soi.dispatched = True
            soi.save()

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse("invoices-view_invoice", args=[self.pk])

    def save(self, *args, **kwargs):
        if self.location is None:
            self.location = self.order.location

        if self.pk is None:
            description = _(u'Order %s dispatched') % self.order.code
            self.order.notify('dispatched', description, self.created_by)

        return super(Invoice, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-id',)
        app_label = 'servo'
        get_latest_by = "id"


class InvoiceItem(AbstractOrderItem):
    invoice = models.ForeignKey(Invoice)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Sales Price")
    )

    @classmethod
    def from_soi(cls, soi, invoice, invoice_item=None):
        """
        Copies SalesOrderItem into an InvoiceItem
        """
        if invoice_item:
            i = invoice_item
        else:
            i = cls(invoice=invoice)

        i.sn = soi.sn
        i.code = soi.code
        i.title = soi.title
        i.price = soi.price
        i.amount = soi.amount
        i.product = soi.product
        i.description = soi.description
        i.created_by = invoice.created_by
        i.save()
        return i

    class Meta:
        app_label = "servo"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice)
    METHODS = (
        (0, _("No Charge")),
        (1, _("Cash")),
        (2, _("Invoice")),
        (3, _("Credit Card")),
        (4, _("Mail payment")),
        (5, _("Online payment"))
    )
    method = models.IntegerField(
        choices=METHODS,
        default=METHODS[0][0],
        verbose_name=_("Payment Method")
    )
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        invoice = self.invoice
        
        if self.method > 0:
            description = _(u'Payment for %0.2f received') % self.amount
            invoice.order.notify('paid', description, self.created_by)

        if invoice.paid_at is None:
            if invoice.get_payment_total() == invoice.total_gross:
                invoice.paid_at = timezone.now()
                invoice.save()

    class Meta:
        app_label = "servo"
