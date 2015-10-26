# -*- coding: utf-8 -*-

from datetime import timedelta
from django.db import models, IntegrityError

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.fields import GenericRelation

from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, post_save, post_delete

from servo import defaults
from servo.lib.shorturl import encode_url

from servo.models.common import Tag, Location, Event, Configuration, GsxAccount
from servo.models.product import *
from servo.models.customer import Customer
from servo.models.device import Device
from servo.models.queue import Queue, Status, QueueStatus


class Order(models.Model):
    """
    The Service Order
    """
    code = models.CharField(max_length=8, unique=True, null=True)
    url_code = models.CharField(max_length=8, unique=True, null=True)
    # Device description or something else
    description = models.CharField(max_length=128, default="")
    status_icon = models.CharField(max_length=16, default="undefined")

    priority = models.IntegerField(
        default=Queue.PRIO_NORMAL,
        choices=Queue.PRIORITIES,
        verbose_name=_("priority")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name="created_orders",
        on_delete=models.SET_NULL
    )

    started_at = models.DateTimeField(null=True)
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name="started_orders",
        on_delete=models.SET_NULL
    )

    closed_at = models.DateTimeField(null=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='closed_orders',
        on_delete=models.SET_NULL
    )
    followed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="followed_orders"
    )

    tags = models.ManyToManyField(Tag, verbose_name="tags")
    events = GenericRelation(Event)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.PROTECT
    )

    checkin_location = models.ForeignKey(
        Location,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    checkout_location = models.ForeignKey(
        Location,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    place = models.CharField(default='', max_length=128)
    customer = models.ForeignKey(
        Customer,
        null=True,
        related_name='orders',
        on_delete=models.SET_NULL
    )
    customer_name = models.CharField(max_length=128, default='')

    devices = models.ManyToManyField(Device, through="OrderDevice")
    products = models.ManyToManyField(Product, through="ServiceOrderItem")

    queue = models.ForeignKey(
        Queue,
        null=True,
        verbose_name=_("queue"),
        on_delete=models.SET_NULL
    )
    status = models.ForeignKey(
        QueueStatus,
        null=True,
        verbose_name=_("status"),
        on_delete=models.SET_NULL
    )

    statuses = models.ManyToManyField(
        Status,
        through="OrderStatus",
        related_name="orders"
    )

    STATE_QUEUED    = 0 # order hasn't been started
    STATE_OPEN      = 1 # order is being worked on
    STATE_CLOSED    = 2 # order is closed
    STATE_WAITING   = 3 # order is waiting (do not track duration)

    STATES = (
        (STATE_QUEUED,   _("Unassigned")),
        (STATE_OPEN,     _("Open")),
        (STATE_CLOSED,   _("Closed")),
        (STATE_WAITING,  _("Waiting"))
    )

    state = models.IntegerField(default=STATE_QUEUED, choices=STATES)
    
    status_name = models.CharField(max_length=128, default="")
    status_started_at = models.DateTimeField(null=True)
    status_limit_green = models.DateTimeField(null=True)  # turn yellow after this
    status_limit_yellow = models.DateTimeField(null=True) # turn red after this
    
    api_fields = ('status_name', 'status_description',)

    def get_issues(self):
        return self.note_set.filter(type=1)

    def apply_rules(self):
        pass

    def get_accessories(self):
        return Accessory.objects.filter(order=self)

    def set_accessories(self, accs, device):
        for a in accs:
            a = Accessory(name=a, order=self, device=device)
            a.save()

    def add_tag(self, tag, user):
        from servo.tasks import apply_rules
        
        if not isinstance(tag, Tag):
            tag = Tag.objects.get(pk=tag)

        self.tags.add(tag)

        event = Event(content_object=self)
        event.description = str(tag.pk)
        event.action = "set_tag"
        event.triggered_by = user

        apply_rules(event)

    def set_tags(self, tags, user):
        return [self.add_tag(t, user) for t in tags]

    def check_in(self, user):
        """
        Checks this Order in through the check-in process
        """
        queue_id = Configuration.conf('checkin_queue')
        self.set_queue(queue_id, user)

    def can_order_products(self):
        return self.products.count() > 0 and self.is_editable

    def duplicate(self, user):
        new_order = Order(customer=self.customer, created_by=user)
        new_order.save()
        new_order.set_queue(self.queue_id, user)

        for d in self.devices.all():
            new_order.add_device(d, user)

        return new_order

    def get_print_template(self, kind="confirmation"):
        template = "orders/print_%s.html" % kind

        if self.queue:
            queue = self.queue

            if kind == "confirmation" and queue.order_template:
                template = queue.order_template.name
            if kind == "quote" and queue.quote_template:
                template = queue.quote_template.name
            if kind == "receipt" and queue.receipt_template:
                template = queue.receipt_template.name
            if kind == "dispatch" and queue.dispatch_template:
                template = queue.dispatch_template.name

        return template

    def get_repairs(self):
        # Returns the active GSX repairs for this SO
        return self.repair_set.exclude(submitted_at=None)

    def get_repair(self):
        # Returns the latest GSX repair for this SO
        try:
            return self.get_repairs().latest()
        except Exception:
            return

    def get_similar(self, status, state):
        # Returns a queryset of "similar" cases
        if self.user is None:
            return Order.objects.filter(status=status)

        return Order.objects.filter(user=self.user)

    def get_footer(self):
        footer = self.code
        repair = self.get_repair()
        if repair:
            footer += ' (%s)' % repair.confirmation
        return footer

    def add_device(self, device, user):
        try:
            OrderDevice.objects.create(order=self, device=device)
            event = _(u'%s added') % device.description
            self.notify('device_added', event, user)
            return event
        except IntegrityError:
            raise ValueError(_("This device has already been added to this order"))

    def add_device_sn(self, sn, user):
        """
        Adds device to order using serial number
        """
        sn = sn.upper()
        device = Device.objects.filter(sn=sn).first()
        
        if device is None:
            device = Device.from_gsx(sn)
            device.save()

        self.add_device(device, user)
        return device

    def remove_device(self, device, user):
        OrderDevice.objects.filter(order=self, device=device).delete()
        msg = _(u'%s removed') % device.description
        self.notify('device_removed', msg, user)
        return msg

    def get_available_users(self, user):
        """
        Returns a list of users available to work on this order
        """
        if self.queue:
            return self.queue.user_set.filter(is_active=True)

        return user.location.user_set.filter(is_active=True)

    def get_title(self):
        """
        Returns a human-readable title for this order, based on various criteria
        """
        from django.utils.timesince import timesince
        now = timezone.now()
        moment_seconds = 120

        if self.closed_at:
            if (now - self.closed_at).seconds < moment_seconds:
                return _("Closed a moment ago")

            return _(u"Closed for %(time)s") % {'time': timesince(self.closed_at)}

        if self.status and self.status_started_at is not None:
            if (now - self.status_started_at).seconds < moment_seconds:
                return _(u"%s a moment ago") % self.status.status.title
            delta = timesince(self.status_started_at)
            d = {'status': self.status.status.title, 'time': delta}
            return _("%(status)s for %(time)s" % d)

        if self.user is None:
            if (now - self.created_at).seconds < moment_seconds:
                return _("Created a moment ago")
            return _("Unassigned for %(delta)s") % {'delta': timesince(self.created_at)}

        if self.in_progress():
            if (now - self.started_at).seconds < moment_seconds:
                return _("Started a moment ago")

            return _("Open for %(delta)s") % {'delta': timesince(self.started_at)}

    def in_progress(self):
        return self.started_at and self.user is not None

    def get_place(self):
        return self.place or _("Select place")

    def get_status(self):
        return self.status or _("Select status")

    def get_user_name(self):
        if self.user is not None:
            return self.user.get_full_name()

    def get_user(self):
        return self.user or _("Select user")

    def get_queue(self):
        return self.queue or _("Select queue")

    def get_queue_url(self):
        if self.queue is not None:
            return self.queue.get_absolute_url()

        return reverse("orders-index")

    def get_queue_title(self):
        if self.queue is not None:
            return self.queue.title
        else:
            return _("Orders")

    def is_item_complete(self, item):
        try:
            return self.checklistitemvalue_set.get(item=item)
        except Exception:
            return False

    def close(self, user):
        self.notify("close_order", _(u"Order %s closed") % self.code, user)
        self.closed_by = user
        self.closed_at = timezone.now()
        self.state = self.STATE_CLOSED
        self.save()

        if Configuration.autocomplete_repairs():
            for r in self.repair_set.filter(completed_at=None):
                r.close(user)

        if self.queue and self.queue.status_closed:
            self.set_status(self.queue.status_closed, user)

    def reopen(self, user):
        self.state = Order.STATE_OPEN
        self.closed_at = None
        self.save()
        msg = _("Order %s reopened") % self.code
        self.notify("reopen", msg, user)
        return msg

    def notes(self):
        return self.note_set.all()

    def reported_notes(self):
        return self.note_set.filter(is_reported=True)

    @property
    def can_create_carryin(self):
        return self.customer and self.queue and self.is_editable

    def get_status_name(self):
        try:
            return self.status.status.title
        except Exception:
            pass

    def get_status_description(self):
        if self.status is None:
            return _('Order is waiting to be processed')
        else:
            return self.status.status.description

    def get_status_id(self):
        """
        Returns "real" status ID of this order (regardless of queue)
        """
        if self.status:
            return self.status.status.id

    def get_next(self):
        try:
            result = Order.objects.filter(pk__gt=self.pk, queue=self.queue)
            return result[0].pk
        except Exception:
            pass

    def get_prev(self):
        try:
            result = Order.objects.filter(pk__lt=self.pk, queue=self.queue)
            return result[0].pk
        except Exception:
            pass

    def get_color(self):
        color = "undefined"
        if self.status:
            now = timezone.now()
            if now > self.status_limit_yellow:
                color = "danger"
            if now < self.status_limit_yellow:
                color = "warning"
            if now < self.status_limit_green:
                color = "success"

        return color

    def get_status_img(self):
        color = self.get_color()
        return "images/status_%s_16.png" % color

    def set_property(self, key, value):
        pass

    def set_location(self, new_location, user):
        # move the products too
        for soi in self.serviceorderitem_set.all():
            product = soi.product

            try:
                source = Inventory.objects.get(location=self.location, product=product)
                source.move(new_location, soi.amount)
            except Inventory.DoesNotExist:
                pass # @TODO: Is this OK?

        self.location = new_location
        msg = _(u"Order %s moved to %s") % (self.code, new_location.title)
        self.notify("set_location", msg, user)
        self.save()

        return msg

    def set_checkin_location(self, new_location, user):
        pass

    def notify(self, action, message, user):
        """
        Notifies this order of an event
        This is also the hub for automation handling
        """
        if self.is_closed:
            return

        e = Event(content_object=self, action=action)
        e.description = message
        e.triggered_by = user
        e.save()

        for f in self.followed_by.exclude(pk=user.pk).exclude(should_notify=False):
            e.notify_users.add(f)

        if action == "product_arrived":
            if self.queue and self.queue.status_products_received:
                new_status = self.queue.status_products_received
                self.set_status(new_status, user)

    def set_status(self, new_status, user):
        """
        Sets status of this order to new_status
        Status can only be set if order belongs to a queue!
        """
        if self.is_closed:
            return # fail silently

        if self.queue is None:
            raise ValueError(_('Order must belong to a queue to set status'))
            
        if isinstance(new_status, QueueStatus):
            status = new_status
        else:
            if int(new_status) == 0:
                return self.unset_status(user)

            status = QueueStatus.objects.get(pk=new_status)

        self.status = status
        self.status_name = status.status.title
        self.status_started_at = timezone.now()

        self.status_limit_green = status.get_green_limit()
        self.status_limit_yellow = status.get_yellow_limit()
        self.save()

        # Set up the OrderStatus
        OrderStatus.create(self, status, user)

        # trigger the notification
        self.notify("set_status", self.status_name, user)

    def unset_status(self, user):
        if self.is_closed:
            return # fail silently

        self.status = None
        self.status_started_at   = None
        self.status_limit_green  = None
        self.status_limit_yellow = None
        self.save()

        self.notify("set_status", _('Status unassigned'), user)

    def set_queue(self, queue_id, user):
        if self.is_closed:
            return

        if queue_id in (None, ''):
            queue_id = 0

        if isinstance(queue_id, Queue):
            queue = queue_id
        else:
            if int(queue_id) == 0:
                return self.unset_queue(user)
                
            queue = Queue.objects.get(pk=queue_id)

        self.queue = queue
        self.priority = queue.priority
        self.notify('set_queue', queue.title, user)

        if queue.gsx_soldto:
            gsx_account = GsxAccount.get_account(self.location, queue)
            for i in self.repair_set.filter(completed_at=None):
                i.gsx_account = gsx_account
                i.save()

        if queue.status_created:
            self.set_status(queue.status_created, user)
        else:
            self.save()

    def unset_queue(self, user):
        self.queue = None
        self.notify('set_queue', _('Removed from queue'), user)
        self.save()

    def add_follower(self, follower):
        if follower in self.followed_by.all():
            return

        self.followed_by.add(follower)

    def remove_follower(self, follower):
        if self.state == self.STATE_CLOSED:
            raise ValueError(_('Closed orders cannot be modified'))

        self.followed_by.remove(follower)

    def toggle_follower(self, follower):
        if follower in order.followed_by.all():
            self.remove_follower(user)
        else:
            self.add_follower(follower)

    def set_user(self, new_user, current_user):
        """
        Sets the assignee of this order to new_user
        """
        if self.state == self.STATE_CLOSED:
            raise ValueError(_('Closed orders cannot be modified'))

        state = self.STATE_OPEN

        if new_user is None:
            state = self.STATE_QUEUED
            event = _("Order unassigned")
            self.remove_follower(self.user)
        else:
            data = {'order': self.code, 'user': new_user.get_full_name()}
            event = _(u"Order %(order)s assigned to %(user)s") % data
            # The assignee should also be a follower
            self.add_follower(new_user)

        self.user = new_user
        self.state = state

        self.notify("set_user", event, current_user)

        if self.user is not None:
            self.location = new_user.location
            if self.started_by is None:
                self.started_by = new_user
                self.started_at = timezone.now()
                queue = self.queue
                if queue and queue.status_assigned:
                    self.set_status(queue.status_assigned, current_user)

        self.save()

    def customer_id(self):
        return self.customer.id

    def customer_list(self):
        """
        Returns this order's customer wrapped in a list for easier
        tree recursion
        """
        return [self.customer]

    def customer_tree(self):
        if self.customer is None:
            return '0'
        else:
            return self.customer.tree_id

    def has_devices(self):
        return self.devices.all().count() > 0

    def device_name(self):
        if self.devices.count():
            return self.devices.all()[0].description

    def set_customer(self, new_customer):
        self.customer = new_customer
        self.save()

    def get_customer_name(self):
        try:
            return self.customer.fullname
        except AttributeError:
            pass

    def device_slug(self):
        try:
            return self.devices.all()[0].slug
        except Exception:
            pass

    def net_total(self):
        total = 0

        for p in self.serviceorderitem_set.filter(should_report=True):
            total += p.price_notax() * p.amount

        return total

    def gross_total(self):
        total = 0

        for p in self.serviceorderitem_set.filter(should_report=True):
            total += p.price * p.amount

        return total

    def total_tax(self):
        return self.gross_total() - self.net_total()

    def add_product(self, product, amount, user):
        """
        Adds this product to the Service Order with stock price
        """
        oi = ServiceOrderItem(order=self, created_by=user)
        oi.product = product
        oi.code = product.code
        oi.title = product.title
        oi.description = product.description
        oi.amount = amount

        oi.price_category = 'stock'
        oi.price = product.price_sales_stock

        oi.save()

        self.notify("product_added", _('Product %s added') % oi.title, user)

        return oi

    def remove_product(self, oi, user):
        oi.delete()
        msg = _('Product %s removed from order') % oi.title
        self.notify("product_removed", msg, user)
        return msg

    @property
    def can_dispatch(self):
        undispatched = self.products.filter(dispatched=False)
        return undispatched.count() > 0 and self.is_editable

    @property
    def can_close(self):
        return self.is_editable and not self.can_dispatch

    def dispatch(self, invoice, products):
        """
        Dispatch these products from the inventory with this invoice
        """
        invoice.dispatch(products)
        if self.queue and self.queue.status_dispatched:
            self.set_status(self.queue.status_dispatched, invoice.created_by)

    def total_margin(self):
        """
        Calculates the total margin for this Service Order
        """
        total_purchase_price = 0
        for p in self.serviceorderitem_set.filter(should_report=True):
            total_purchase_price += p.get_product_price('purchase') * p.amount

        return (self.net_total() - Decimal(total_purchase_price))

    @property
    def products(self):
        return self.serviceorderitem_set.filter(should_report=True)

    @property
    def serialized_products(self):
        return self.products.filter(product__is_serialized=True)

    def get_parts(self):
        """
        Returns the GSX parts that can be ordered for this SRO
        """
        return [x for x in self.products.all() if x.product.is_apple_part]

    @property
    def has_parts(self):
        return len(self.get_parts()) > 0

    def get_devices(self):
        return self.devices.filter(orderdevice__should_report=True)

    def get_first_device(self):
        try:
            return self.get_devices().first()
        except Exception:
            pass

    @property
    def is_editable(self):
        return self.closed_at is None

    @property
    def is_closed(self):
        return self.closed_at is not None

    @property
    def has_products(self):
        return self.products.count() > 0

    def has_accessories(self):
        return self.accessory_set.all().count() > 0

    def get_accessories(self):
        return self.accessory_set.values_list('name', flat=True)

    class Meta:
        app_label = 'servo'
        ordering = ('-priority', 'id',)

        permissions = (
            ("change_user",     _("Can set assignee")),
            ("change_status",   _("Can change status")),
            ("follow_order",    _("Can follow order")),
            ("copy_order",      _("Can copy order")),
            ("batch_process",   _("Can batch process")),
        )

    def save(self, *args, **kwargs):

        location = self.created_by.location

        if self.location_id is None:
            self.location = location
            
        if self.checkin_location is None:
            self.checkin_location = location

        if self.checkout_location is None:
            self.checkout_location = location

        if self.customer and self.customer_name == '':
            self.customer_name = self.customer.fullname

        super(Order, self).save(*args, **kwargs)

        if self.code is None:
            self.url_code = encode_url(self.id).upper()
            self.code = settings.INSTALL_ID + str(self.id).rjust(6, '0')
            event = _('Order %s created') % self.code
            self.notify('created', event, self.created_by)
            self.save()

    def get_absolute_url(self):
        return reverse("orders-edit", args=[self.pk])

    def __unicode__(self):
        return self.code


class AbstractOrderItem(models.Model):
    """
    The base class for order lines (purchase, sales)
    """
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    code = models.CharField(blank=True, default='', max_length=128)
    title = models.CharField(max_length=128, verbose_name=_("title"))
    description = models.TextField(
        blank=True,
        default='',
        verbose_name=_("description")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        editable=False,
        on_delete=models.SET_NULL
    )

    amount = models.IntegerField(default=1, verbose_name=_("amount"))
    sn = models.CharField(
        blank=True,
        default="",
        max_length=32,
        verbose_name=_("KGB Serial Number")
    )

    def price_notax(self):
        """
        Returns the price of this OI w/o VAT
        """
        from decimal import ROUND_05UP
        vat_pct = self.product.pct_vat
        return (self.price/Decimal((100+vat_pct)/100)).quantize(Decimal('1.00'))

    def total_gross(self):
        return self.price * self.amount

    def total_net(self):
        return self.price_notax() * self.amount

    def total_tax(self):
        """
        Returns the amount of VAT paid for this POI
        """
        return (self.price - self.price_notax()) * self.amount

    class Meta:
        abstract = True


class ServiceOrderItem(AbstractOrderItem):
    """
    A product that has been added to a Service Order
    """
    order = models.ForeignKey(Order)

    dispatched = models.BooleanField(
        default=False,
        verbose_name=_("dispatched")
    )
    should_report = models.BooleanField(
        default=True,
        verbose_name=_("report")
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_('sales price')
    )

    replaced_at = models.DateTimeField(null=True)
    replaced_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        editable=False,
        related_name='replaced_parts'
    )

    kbb_sn = models.CharField(
        blank=True,
        default="",
        max_length=32,
        verbose_name=_("KBB Serial Number")
    )

    imei = models.CharField(
        blank=True,
        default="",
        max_length=35,
        verbose_name=_("IMEI")
    )

    PRICE_CATEGORIES = (
        ('warranty', _("Warranty")),
        ('exchange', _("Exchange Price")),
        ('stock', _("Stock Price")),
    )

    price_category = models.CharField(
        max_length=32,
        choices=PRICE_CATEGORIES,
        default=PRICE_CATEGORIES[0],
        verbose_name=_("Price category")
    )

    comptia_code = models.CharField(
        blank=True,
        default="",
        max_length=4,
        verbose_name=_("symptom code")
    )
    comptia_modifier = models.CharField(
        blank=True,
        default="",
        max_length=1,
        verbose_name=_("symptom modifier")
    )

    def can_create_device(self):
        pt = self.product.part_type
        return pt == 'REPLACEMENT' and self.sn

    def comptia_choices(self):
        if self.product is not None:
            from servo.models.parts import symptom_codes
            return symptom_codes(self.product.component_code)

    def get_comptia_code_display(self):
        for i in self.comptia_choices():
            if i[0] == self.comptia_code:
                return i[1]

    def get_comptia_modifier_display(self):
        if self.comptia_modifier:
            from servo.models.parts import symptom_modifiers
            for m in symptom_modifiers():
                if m[0] == self.comptia_modifier:
                    return m[1]

    def get_part(self):
        return self.servicepart_set.latest()

    def get_poitem(self):
        return self.purchaseorderitem_set.latest()

    def get_repair(self):
        return self.order.repair_set.latest()

    def reserve_product(self):
        """
        Reserve this SOI for the inventory at this location
        """
        location = self.order.location
        inventory, created = Inventory.objects.get_or_create(location=location, 
                                                             product=self.product)
        inventory.amount_reserved += self.amount
        inventory.save()

    def get_purchase_price(self):
        """
        Returns the purchase price of this SOIs Product
        """
        return self.product.get_price(self.price_category, "purchase")

    def get_product_price(self, kind):
        return self.product.get_price(category=self.price_category, kind=kind)

    def save(self, *args, **kwargs):
        self.sn = self.sn.upper()
        self.kbb_sn = self.kbb_sn.upper()
        return super(ServiceOrderItem, self).save(*args, **kwargs)

    @property
    def is_abused(self):
        return self.price_category == 'stock'

    @property
    def is_warranty(self):
        return self.price_category == 'warranty'

    def __unicode__(self):
        return self.code

    class Meta:
        app_label = "servo"
        ordering = ('id',)
        get_latest_by = "id"


class OrderStatus(models.Model):
    """
    The M/M statuses of an order
    """
    order = models.ForeignKey(Order)
    status = models.ForeignKey(Status)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)

    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='+'
    )
    finished_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='+'
    )

    green_limit = models.DateTimeField(null=True)
    yellow_limit = models.DateTimeField(null=True)

    BADGES = (
        ('undefined',   'undefined'),
        ('success',     'success'),
        ('warning',     'warning'),
        ('danger',      'danger'),
    )

    badge = models.CharField(choices=BADGES, default=BADGES[0][0], max_length=16)
    duration = models.IntegerField(default=0)

    @classmethod
    def create(cls, order, queue_status, user):
        """
        Set status or order to queue_status.status
        """
        new_status = queue_status.status
        os = cls(order=order, status=new_status)
        os.started_by = user
        #os.started_at = timezone.now()

        os.green_limit = queue_status.get_green_limit()
        os.yellow_limit = queue_status.get_yellow_limit()

        os.save()

        prev = os.get_previous()

        if prev is None:
            return

        # set color of previous OS
        if prev.finished_by is None:
            prev.finished_by = user
            prev.finished_at = timezone.now()
            prev.duration = (prev.finished_at - prev.started_at).total_seconds()

        prev.badge = prev.get_badge()
        prev.save()

    def get_badge(self):
        now = timezone.now()
        badge = "undefined"
        if self.yellow_limit and now > self.yellow_limit:
            badge = "danger"
        if self.yellow_limit and now < self.yellow_limit:
            badge = "warning"
        if self.green_limit and now < self.green_limit:
            badge = "success"

        return badge

    def get_next(self):
        statuses = self.order.orderstatus_set
        return statuses.filter(started_at__gt=self.started_at).order_by('id').first()

    def get_previous(self):
        statuses = self.order.orderstatus_set
        return statuses.filter(started_at__lt=self.started_at).order_by('id').last()

    def __unicode__(self):
        return self.status.title

    class Meta:
        app_label = "servo"
        ordering = ('-started_at',)
        get_latest_by = "started_at"


class OrderDevice(models.Model):
    """
    A device attached to a service order
    """
    order = models.ForeignKey(Order)
    device = models.ForeignKey(Device)
    should_report = models.BooleanField(default=True)

    def is_repeat_service(self):
        from django.utils import timezone
        created_at = self.order.created_at
        tlimit = timezone.now() - timedelta(days=30)
        orders = Order.objects.filter(orderdevice__device=self.device,
                                      created_at__lt=created_at,
                                      created_at__gte=tlimit)

        return orders.exclude(pk=self.order.pk).count() > 0

    class Meta:
        app_label = "servo"
        unique_together = ('order', 'device', ) # Can't add the same device more than once


class Accessory(models.Model):
    """
    An accessory that came with the device in this Service Order
    """
    name    = models.TextField()
    qty     = models.IntegerField(default=1)
    device  = models.ForeignKey(Device)
    order   = models.ForeignKey(Order)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "servo"


@receiver(post_save, sender=OrderDevice)
def trigger_orderdevice_saved(sender, instance, created, **kwargs):
    order = instance.order
    device = instance.device
    order.description = device.description

    if order.queue is None:
        pass # @TODO try to autoasign case to right queue...

    order.save()


@receiver(post_delete, sender=OrderDevice)
def trigger_device_removed(sender, instance, **kwargs):
    try:
        order = instance.order
    except Order.DoesNotExist:
        return # Means the whole order was deleted, not just the device

    devices = order.devices.all()

    if devices.count() > 0:
        order.description = devices[0].description
    else:
        order.description = ''

    order.save()
