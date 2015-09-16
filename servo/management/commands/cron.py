# -*- coding: utf-8 -*-

import gsxws
from datetime import date, timedelta

from django.conf import settings
from django.core.files import File
from django.utils.translation import ugettext as _

from django.core.management.base import BaseCommand

from django.db.models import F
from django.utils import timezone
from django.core.cache import cache

from servo.models.common import Configuration, Location, CsvTable, GsxAccount
from servo.models import Inventory, Order, PurchaseOrder, User


def send_table(sender, recipient, subject, table, send_empty=False):
    from django.core.mail import send_mail
    if not send_empty and not table.has_body():
        return

    config = Configuration.conf()
    settings.EMAIL_HOST = config.get('smtp_host')
    settings.EMAIL_USE_TLS = config.get('smtp_ssl')
    settings.EMAIL_HOST_USER = config.get('smtp_user')
    settings.EMAIL_HOST_PASSWORD = config.get('smtp_password')

    send_mail(subject, unicode(table), sender, [recipient], fail_silently=False)


class Command(BaseCommand):
    help = "Runs Servo's periodic commands"

    def update_invoices(self):
        uid = Configuration.conf('imap_act')
        user = User.objects.get(pk=uid)

        for a in GsxAccount.objects.all():
            try:
                a.default(user)
                lookup = gsxws.Lookup(shipTo=a.ship_to, invoiceDate=date.today())
                invoices = lookup.invoices()
                for i in invoices:
                    details = gsxws.Lookup(invoiceID=i).invoice_details()
                    # @TODO: What about stock orders?
                    po = PurchaseOrder.objects.get(pk=details.purchaseOrderNumber)
                    po.invoice_id = i
                    po.invoice.save("%s.pdf" % i, File(open(details.invoiceData)))
            except Exception, e:
                raise e

    def update_warranty(self):
        pass

    def notify_aging_repairs(self):
        """
        Reports on cases that have been red for a day
        """
        conf = Configuration.conf()

        try:
            sender = conf['default_sender']
        except KeyError:
            raise ValueError('Default sender address not defined')

        now = timezone.now()
        limit = now - timedelta(days=1)

        for l in Location.objects.filter(enabled=True):
            table = CsvTable()
            table.addheader(['Order', 'Assigned To', 'Status', 'Days red'])

            # "Aging" repairs are ones that have been red for at least a day
            orders = Order.objects.filter(
                location=l,
                state__lt=Order.STATE_CLOSED,
                status_limit_yellow__lt=limit
            )

            for o in orders:
                username = o.get_user_name() or _("Unassigned")
                status_title = o.get_status_name() or _("No Status")
                days = (now - o.status_limit_yellow).days
                table.addrow([o.code, username, status_title, days])

            subject = _(u"Repairs aging beyond limits at %s") % l.title

            if Configuration.notify_location():
                send_table(sender, l.email, subject, table)
            if Configuration.notify_email_address():
                send_table(sender, conf['notify_address'], subject, table)

    def notify_stock_limits(self):
        conf = Configuration.conf()

        try:
            sender = conf['default_sender']
        except KeyError:
            raise ValueError('Default sender address not defined')

        for l in Location.objects.filter(enabled=True):
            out_of_stock = Inventory.objects.filter(
                location=l,
                amount_stocked__lt=F('amount_minimum')
            )

            table = CsvTable()
            table.addheader(['Product', 'Minimum', 'Stocked'])

            for i in out_of_stock:
                table.addrow([i.product.code, i.amount_minimum, i.amount_stocked])

            subject = _(u"Products stocked below limit")

            if Configuration.notify_location():
                send_table(sender, l.email, subject, table)
            if Configuration.notify_email_address():
                send_table(sender, conf['notify_address'], subject, table)

    def update_counts(self):
        now = timezone.now()
        orders = Order.objects.filter(state__lt=Order.STATE_CLOSED)
        green = orders.filter(status_limit_green__gte=now)
        cache.set('green_order_count', green.count())
        yellow = orders.filter(status_limit_yellow__gte=now)
        cache.set('yellow_order_count', yellow.count())
        red = orders.filter(status_limit_yellow__lte=now)
        cache.set('red_order_count', red.count())

    def handle(self, *args, **options):
        #self.update_invoices()
        self.update_counts()
        self.notify_aging_repairs()
        self.notify_stock_limits()
