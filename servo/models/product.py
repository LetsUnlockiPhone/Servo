# -*- coding: utf-8 -*-

import re
from os.path import basename

from django.db import models
from django.db import connection
from django.conf import settings
from django.core.files import File
from django.core.cache import cache
from decimal import Decimal, ROUND_CEILING
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from django.contrib.contenttypes.fields import GenericRelation

from django.utils.translation import ugettext_lazy as _

from mptt.managers import TreeManager
from gsxws import comptia, parts, validate
from mptt.models import MPTTModel, TreeForeignKey

from servo import defaults
from servo.lib.shorturl import from_time
from servo.models import Configuration, Location, TaggedItem


def get_margin(price=0.0):
    """
    Returns the proper margin % for this price
    """
    price  = Decimal(price)
    margin = defaults.margin()

    try:
        return Decimal(margin)
    except Exception:
        ranges = margin.split(';')
        for r in ranges:
            m = re.search(r'(\d+)\-(\d+)=(\d+)', r)
            p_min, p_max, margin = m.groups()
            if Decimal(p_min) <= price <= Decimal(p_max):
                return Decimal(margin)

    return Decimal(margin)


def default_vat():
    conf = Configuration.conf()
    return conf.get("pct_vat", 0.0)


def inventory_totals():
    """
    Returns the total purchase and sales value
    of our inventory
    """
    cursor = connection.cursor()
    sql = """SELECT SUM(price_purchase_stock*total_amount) AS a,
    SUM(price_sales_stock*total_amount) AS b
    FROM servo_product
    WHERE part_type != 'SERVICE'"""
    cursor.execute(sql)

    for k, v in cursor.fetchall():
        return (k, v)


class DeviceGroup(models.Model):
    """
    This links products with devices.
    The title should match a device's description field
    """
    title = models.CharField(max_length=128, unique=True)

    class Meta:
        app_label = "servo"


class AbstractBaseProduct(models.Model):
    code = models.CharField(
        unique=True,
        max_length=32,
        default=from_time,
        verbose_name=_("Code")
    )

    subst_code = models.CharField(
        default='',
        max_length=32,
        editable=False,
        verbose_name=_("Substituted (new) code of this part")
    )

    title = models.CharField(
        max_length=255,
        default=_("New Product"),
        verbose_name=_("Title")
    )
    description = models.TextField(
        default='',
        blank=True,
        verbose_name=_("Description")
    )
    pct_vat = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=default_vat,
        verbose_name=_("VAT %")
    )

    fixed_price = models.BooleanField(
        default=False,
        help_text=_("Don't update price when recalculating prices or importing parts")
    )

    price_purchase_exchange = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Purchase price")
    )

    pct_margin_exchange = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=get_margin,
        verbose_name=_("Margin %")
    )
    price_notax_exchange = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Net price"),
        help_text=_("Purchase price + margin %")
    )
    price_sales_exchange = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Sales price"),
        help_text=_("Purchase price + margin % + shipping + VAT %")
    )

    price_purchase_stock = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Purchase price")
    )
    pct_margin_stock = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=get_margin,
        verbose_name=_("Margin %")
    )
    price_notax_stock = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Net price"),
        help_text=_("Purchase price + margin %")
    )
    price_sales_stock = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Sales price"),
        help_text=_("Purchase price + margin % + shipping + VAT %")
    )

    is_serialized = models.BooleanField(
        default=False,
        verbose_name=_('Is serialized'),
        help_text=_("Product has a serial number")
    )

    class Meta:
        app_label = 'servo'
        abstract = True


class Product(AbstractBaseProduct):
    """
    An item in the inventory
    """
    warranty_period = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Warranty (months)")
    )
    shelf = models.CharField(
        default='',
        blank=True,
        max_length=8,
        verbose_name=_("Shelf code")
    )
    brand = models.CharField(
        default='',
        blank=True,
        max_length=32,
        verbose_name=_("Brand")
    )
    categories = models.ManyToManyField(
        "ProductCategory",
        blank=True,
        verbose_name=_("Categories")
    )
    device_models = models.ManyToManyField(
        "DeviceGroup",
        blank=True,
        verbose_name=_("Device models")
    )
    tags = GenericRelation(TaggedItem)
    photo = models.ImageField(
        null=True,
        blank=True,
        upload_to="products",
        verbose_name=_("Photo")
    )

    shipping = models.FloatField(default=0, verbose_name=_('Shipping'))

    # component code is used to identify Apple parts
    component_code = models.CharField(
        blank=True,
        default='',
        max_length=1,
        choices=comptia.GROUPS,
        verbose_name=_("Component group")
    )

    labour_tier = models.CharField(max_length=15, blank=True, default='')

    # We need this to call the correct GSX SN Update API
    PART_TYPES = (
        ('ADJUSTMENT',  _("Adjustment")),
        ('MODULE',      _("Module")),
        ('REPLACEMENT', _("Replacement")),
        ('SERVICE',     _("Service")),
        ('SERVICE CONTRACT', _("Service Contract")),
        ('OTHER',       _("Other")),
    )

    part_type = models.CharField(
        max_length=18,
        default='OTHER',
        choices=PART_TYPES,
        verbose_name=_("Part type")
    )

    eee_code = models.CharField(
        blank=True,
        default='',
        max_length=256,
        verbose_name=_("EEE code")
    )

    total_amount = models.IntegerField(editable=False, default=0)

    def get_pick_url(self, order, device=None):
        pk = self.pk or self.code
        return '/orders/%d/devices/%d/'

    def is_service(self):
        return self.part_type == 'SERVICE'

    def get_warranty_display(self):
        if self.warranty_period:
            return _("%d months") % self.warranty_period

    def can_order_from_gsx(self):
        ok_types = ("MODULE", "REPLACEMENT", "OTHER",)
        return self.component_code and self.part_type in ok_types

    def can_update_price(self):
        return self.can_order_from_gsx() and not self.fixed_price

    def update_price(self, new_product=None):
        """
        Updates part's price info from GSX or to match new_product
        """
        if new_product is None:
            part = parts.Part(partNumber=self.code).lookup()
            new_product = Product.from_gsx(part)

        self.price_purchase_exchange = new_product.price_purchase_exchange
        self.price_purchase_stock = new_product.price_purchase_stock

        self.title = new_product.title

        self.component_code = new_product.component_code

        self.price_notax_stock = new_product.price_notax_stock
        self.price_notax_exchange = new_product.price_notax_exchange

        self.pct_margin_stock = new_product.pct_margin_stock
        self.pct_margin_exchange = new_product.pct_margin_exchange

        self.price_sales_stock = new_product.price_sales_stock
        self.price_sales_exchange = new_product.price_sales_exchange

        self.save()

    def calculate_price(self, price, shipping=0.0):
        """
        Calculates price and returns it w/ and w/o tax
        """
        conf = Configuration.conf()
        shipping = shipping or 0.0

        if not isinstance(shipping, Decimal):
            shipping = Decimal(shipping)

        margin = get_margin(price)
        vat = Decimal(conf.get("pct_vat", 0.0))

        # TWOPLACES = Decimal(10) ** -2  # same as Decimal('0.01')
        # @TODO: make rounding configurable!
        wo_tax = ((price*100)/(100-margin)+shipping).to_integral_exact(rounding=ROUND_CEILING)
        with_tax = (wo_tax*(vat+100)/100).to_integral_exact(rounding=ROUND_CEILING)

        return wo_tax, with_tax

    def set_stock_sales_price(self):
        if not self.price_purchase_stock or self.fixed_price:
            return

        purchase_sp = self.price_purchase_stock
        sp, vat_sp  = self.calculate_price(purchase_sp, self.shipping)
        self.price_notax_stock = sp
        self.price_sales_stock = vat_sp

    def set_exchange_sales_price(self):
        if not self.price_purchase_exchange or self.fixed_price:
            return

        purchase_ep = self.price_purchase_exchange
        ep, vat_ep  = self.calculate_price(purchase_ep, self.shipping)
        self.price_notax_exhcange = ep
        self.price_sales_exchange = vat_ep

    @property
    def is_apple_part(self):
        return validate(self.code, 'partNumber')

    @classmethod
    def from_gsx(cls, part):
        """
        Creates a Servo Product from GSX partDetail.
        We don't do GSX lookups here since we can't
        determine the correct GSX Account at this point.
        """
        conf = Configuration.conf()

        try:
            shipping = Decimal(conf.get("shipping_cost"))
        except TypeError:
            shipping = Decimal(0.0)

        part_number = part.originalPartNumber or part.partNumber
        product = Product(code=part_number)
        product.title = part.partDescription

        if part.originalPartNumber:
            product.subst_code = part.partNumber

        if part.stockPrice and not product.fixed_price:
            # calculate stock price
            purchase_sp = part.stockPrice or 0.0
            purchase_sp = Decimal(purchase_sp)
            sp, vat_sp  = product.calculate_price(purchase_sp, shipping)
            product.pct_margin_stock  = get_margin(purchase_sp)
            product.price_notax_stock = sp
            product.price_sales_stock = vat_sp
            # @TODO: make rounding configurable
            product.price_purchase_stock = purchase_sp.to_integral_exact(
                rounding=ROUND_CEILING
            )

        try:
            # calculate exchange price
            purchase_ep = part.exchangePrice or 0.0
            purchase_ep = Decimal(purchase_ep)

            if purchase_ep > 0 and not product.fixed_price:
                ep, vat_ep = product.calculate_price(purchase_ep, shipping)
                product.price_notax_exchange = ep
                product.price_sales_exchange = vat_ep
                product.pct_margin_exchange = Configuration.get_margin(purchase_ep)
                # @TODO: make rounding configurable
                product.price_purchase_exchange = purchase_ep.to_integral_exact(
                    rounding=ROUND_CEILING
                )
        except AttributeError:
            pass  # Not all parts have exchange prices

        product.brand = "Apple"
        product.shipping = shipping
        product.warranty_period = 3

        product.labour_tier = part.laborTier
        product.part_type = part.partType.upper()

        # EEE and componentCode are sometimes missing
        if part.eeeCode:
            product.eee_code = str(part.eeeCode).strip()
        if part.componentCode:
            product.component_code = str(part.componentCode).strip()

        product.is_serialized = part.isSerialized
        return product

    @classmethod
    def from_cache(cls, code):
        data = cache.get(code)
        return cls.from_gsx(data)

    def get_photo(self):
        try:
            return self.photo.url
        except ValueError:
            from django.conf import settings
            return "%simages/na.gif" % settings.STATIC_URL

    def tax(self):
        return self.price_sales - self.price_notax

    def latest_date_sold(self):
        return '-'

    def latest_date_ordered(self):
        return '-'

    def latest_date_arrived(self):
        return '-'

    def track_inventory(self):
        if not Configuration.track_inventory():
            return False

        if self.part_type == "SERVICE":
            return False

        return True

    def sell(self, amount, location):
        """
        Deduct product from inventory with specified location
        """
        if not self.track_inventory():
            return

        try:
            inventory = Inventory.objects.get(product=self, location=location)
            
            try:
                inventory.amount_stocked  = inventory.amount_stocked - amount
                inventory.amount_reserved = inventory.amount_reserved - amount
            except Exception as e:
                # @TODO: Would be nice to trigger a warning
                pass

            inventory.save()
        except Inventory.DoesNotExist:
            raise ValueError(_(u"Product %s not found in inventory.") % self.code)

    def get_relative_url(self):
        if self.pk is None:
            return "code/%s/" % self.code

        return self.pk

    def get_absolute_url(self):
        if self.pk is None:
            return reverse("products-view_product", kwargs={'code': self.code})

        return reverse("products-view_product", kwargs={'pk': self.pk})

    def get_amount_stocked(self, user):
        """
        Returns the amount of this product in the same location as the user.
        Caches the result for faster access later.
        """
        amount = 0
        track_inventory = Configuration.track_inventory()

        if not track_inventory:
            return 0

        if self.part_type == "SERVICE" or not self.pk:
            return 0

        cache_key = "product_%d_amount_stocked" % self.pk

        if cache.get(cache_key):
            return cache.get(cache_key)

        location = user.get_location()

        try:
            inventory = Inventory.objects.get(product=self, location=location)
            amount = inventory.amount_stocked
        except Inventory.DoesNotExist:
            pass

        cache.set(cache_key, amount)
        return amount

    def get_price(self, category=None, kind="sales"):
        """
        Returns price of product in specific price category
        of the specified kind (sales or purchase)
        """
        prices = dict(
            warranty=0.0,
            exchange=float(getattr(self, "price_%s_exchange" % kind)),
            stock=float(getattr(self, "price_%s_stock" % kind))
        )

        return prices.get(category) if category else prices

    def get_pk(self):
        return self.pk or Product.objects.get(code=self.code).pk

    def update_photo(self):
        """
        Updates this product image with the GSX part image
        """
        if self.component_code and not self.photo:
            try:
                part = parts.Part(partNumber=self.code)
                result = part.fetch_image()
                filename = basename(result)
                self.photo.save(filename, File(open(result)))
            except Exception as e:
                print e

    def __unicode__(self):
        return u'%s %s' % (self.code, self.title)

    class Meta:
        ordering = ('-id',)
        app_label = 'servo'
        permissions = (
            ("change_amount", _("Can change product amount")),
        )


class ProductCategory(MPTTModel):
    site = models.ForeignKey(
        Site,
        editable=False,
        default=defaults.site_id
    )
    title = models.CharField(
        max_length=255,
        unique=True,
        default=_("New Category")
    )
    slug = models.SlugField(null=True, editable=False)
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children'
    )

    objects = TreeManager()

    def get_products(self):
        """
        Returns products under this entire category branch
        """
        return Product.objects.filter(
            categories__lft__gte=self.lft,
            categories__rght__lte=self.rght,
            categories__tree_id=self.tree_id
        )

    def get_product_count(self):
        count = self.product_set.count()
        return count if count > 0 else ""

    def get_absolute_url(self):
        return "/sales/products/%s/" % self.slug

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        self.slug = slugify(self.title[:50])
        return super(ProductCategory, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = "servo"
        get_latest_by = "id"
        ordering = ("-title",)
        unique_together = ("title", "site",)


class Inventory(models.Model):
    """
    Inventory tracks how much of Product X is in Location Y
    """
    product  = models.ForeignKey(Product)
    location = models.ForeignKey(Location)

    amount_minimum = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Minimum amount")
    )
    amount_reserved = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Reserved amount")
    )
    amount_stocked = models.IntegerField(
        default=0,
        verbose_name=_("Stocked amount"),
    )
    amount_ordered = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordered amount")
    )

    def move(self, new_location, amount=1):
        """
        Move this inventory to a new_location
        """
        if new_location == self.location:
            raise ValueError(_('Cannot move products to the same location'))

        target, created = Inventory.objects.get_or_create(location=new_location,
                                                          product=self.product)
        self.amount_stocked = self.amount_stocked - amount
        self.save()
        target.amount_stocked = target.amount_stocked + amount
        target.save()

    def save(self, *args, **kwargs):
        super(Inventory, self).save(*args, **kwargs)
        total_amount = 0

        for i in self.product.inventory_set.all():
            total_amount += i.amount_stocked

        self.product.total_amount = total_amount
        self.product.save()

    class Meta:
        app_label = "servo"
        unique_together = ('product', 'location',)


class ShippingMethod(models.Model):
    """
    How the contents of an order should be shipped
    """
    title = models.CharField(max_length=128, default=_('New Shipping Method'))
    description = models.TextField(default='', blank=True)
    notify_email = models.EmailField(null=True, blank=True)

    class Meta:
        app_label = "servo"
