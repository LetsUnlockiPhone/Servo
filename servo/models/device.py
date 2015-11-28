# -*- coding: utf-8 -*-

import re
import gsxws
from gsxws import diagnostics
from os.path import basename
from django_countries import countries
from django.core.validators import RegexValidator

from django.db import models
from django.conf import settings
from django.core.files import File
from django.core.cache import cache
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save

from django.contrib.contenttypes.fields import GenericRelation

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from servo import defaults
from servo.validators import sn_validator
from servo.models import GsxAccount, Product, DeviceGroup, TaggedItem


class Device(models.Model):
    """
    The serviceable device
    """
    # @TODO: unique=True would be nice, but complicated...
    sn = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_("Serial Number"),
        validators=[sn_validator]
    )
    description = models.CharField(
        max_length=128,
        default=_("New Device"),
        verbose_name=_("Description")
    )
    brand = models.CharField(
        blank=True,
        max_length=128,
        default=_("Apple"),
        verbose_name=_("Brand")
    )
    reseller = models.CharField(
        blank=True,
        default='',
        max_length=128,
        verbose_name=_("Reseller")
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    imei = models.CharField(
        blank=True,
        default='',
        max_length=15,
        verbose_name=_("IMEI Number")
    )
    initial_activation_policy = models.CharField(
        default='',
        editable=False,
        max_length=128,
        verbose_name=_("Initial Activation Policy")
    )
    applied_activation_policy = models.CharField(
        default='',
        editable=False,
        max_length=128,
        verbose_name=_("Applied Activation Policy")
    )
    next_tether_policy = models.CharField(
        default='',
        editable=False,
        max_length=128,
        verbose_name=_("Next Tether Policy")
    )
    unlocked = models.NullBooleanField(default=None, editable=False)
    slug = models.SlugField(null=True, editable=False, max_length=128)
    PRODUCT_LINES = gsxws.products.models()
    LINE_CHOICES = [(k, x['name']) for k, x in PRODUCT_LINES.items()]
    product_line = models.CharField(
        max_length=16,
        default="OTHER",
        choices=LINE_CHOICES,
        verbose_name=_("Product Line")
    )
    products = models.ManyToManyField(
        Product,
        editable=False,
        help_text=_('Products that are compatible with this device instance')
    )
    config_code = models.CharField(default='', max_length=8, editable=False)
    configuration = models.CharField(
        blank=True,
        default='',
        max_length=256,
        verbose_name=_("Configuration")
    )

    WARRANTY_CHOICES = (
        ('QP',  _("Quality Program")),
        ('CS',  _("Customer Satisfaction")),
        ('ALW', _("Apple Limited Warranty")),
        ('APP', _("AppleCare Protection Plan")),
        ('CC',  _("Custom Bid Contracts")),
        ('CBC', _("Custom Bid Contracts")), # sometimes CC, sometimes CBC?
        ('WTY', _("3'rd Party Warranty")),
        ('OOW', _("Out Of Warranty (No Coverage)")),
        ('NA',  _("Unknown")),
    )

    warranty_status = models.CharField(
        max_length=3,
        default="NA",
        choices=WARRANTY_CHOICES,
        verbose_name=_("Warranty Status")
    )
    username = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_("Username")
    )
    password = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_("Password")
    )
    purchased_on = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date of Purchase")
    )
    purchase_country = models.CharField(
        blank=True,
        editable=False,
        max_length=128,
        choices=countries,
        default=defaults.country,
        verbose_name=_("Purchase Country")
    )

    sla_description = models.TextField(null=True, editable=False)
    has_onsite = models.BooleanField(
        default=False,
        help_text=_('Device is eligible for onsite repairs in GSX')
    )
    contract_start_date = models.DateField(null=True, editable=False)
    contract_end_date = models.DateField(null=True, editable=False)
    onsite_start_date = models.DateField(null=True, editable=False)
    onsite_end_date = models.DateField(null=True, editable=False)

    parts_and_labor_covered = models.BooleanField(default=False, editable=False)

    notes = models.TextField(blank=True, default="", verbose_name=_("notes"))
    tags = GenericRelation(TaggedItem)
    photo = models.ImageField(
        null=True,
        blank=True,
        upload_to="devices",
        verbose_name=_("Photo")
    )

    image_url = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("Image URL")
    )
    manual_url = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("Manual URL")
    )
    exploded_view_url = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("Exploded View")
    )

    is_vintage = models.BooleanField(
        default=False,
        verbose_name=_('Vintage'),
        help_text=_('Device is considered vintage in GSX')
    )
    fmip_active = models.BooleanField(default=False, editable=False)
    
    def is_apple_device(self):
        """
        Checks if this is a valid Apple device SN
        """
        valid_sn = gsxws.core.validate(self.sn, 'serialNumber')
        valid_imei = gsxws.core.validate(self.imei, 'alternateDeviceId')
        return valid_sn or valid_imei

    def get_sn(self):
        return self.sn or self.imei

    @property
    def has_warranty(self):
        return self.warranty_status in ('ALW', 'APP', 'CBC',)

    @property
    def tag_choices(self):
        return TaggedItem.objects.filter(content_type__model="device").distinct("tag")

    def add_tags(self, tags):
        tags = [x for x in tags if x != ''] # Filter out empty tags

        if not tags:
            return

        content_type = ContentType.objects.get_for_model(Device)

        for t in tags:
            tag, created = TaggedItem.objects.get_or_create(content_type=content_type,
                                                            object_id=self.pk,
                                                            tag=t)
        tag.save()

    def get_icon(self):
        if re.match('iPad', self.description):
            return "ipad"
        if re.match('iPhone', self.description):
            return "iphone"
        if re.match('iPod shuffle', self.description):
            return "ipod_shuffle"
        if re.match('iPod', self.description):
            return "ipod"
        if re.match('MacBook', self.description):
            return "macbook"

        return "imac"

    def set_wty_status(self, status):
        """
        Translates a GSX warranty status description
        to our internal representation
        """
        if not isinstance(status, basestring):
            return
        if re.match(r"Apple Limited", status):
            self.warranty_status = "ALW"
        if re.match(r"AppleCare", status):
            self.warranty_status = "APP"
        if re.match(r"Customer Satisfaction", status):
            self.warranty_status = "CSC"
        if re.match(r"Custom Bid", status):
            self.warranty_status = "CBC"
        if re.match(r"Out Of", status):
            self.warranty_status = "OOW"

    def to_dict(self):
        result = {'sn': self.sn}
        result['description'] = self.description
        result['warranty_status'] = self.warranty_status
        result['purchased_on'] = self.purchased_on
        result['purchase_country'] = self.purchase_country
        result['username'] = self.username
        result['password'] = self.password
        return result

    @classmethod
    def from_dict(cls, d):
        if d.get('_pk'):
            return cls.objects.get(pk=d['_pk'])

        device = Device()

        for k, v in d:
            if k.startswith('_'):
                continue
            setattr(device, k, v)

        return device

    def to_gsx(self):
        """
        Returns the corresponding gsxws Product object
        """
        if len(self.imei):
            return gsxws.Product(self.imei)
        return gsxws.Product(self.sn)

    @classmethod
    def from_gsx(cls, sn, device=None, cached=True):
        """
        Initialize new Device with warranty info from GSX
        Or update existing one
        """
        sn = sn.upper()
        cache_key = 'device-%s' % sn

        # Only cache unsaved devices
        if cached and device is None:
            if cache.get(cache_key):
                return cache.get(cache_key)

        arg = gsxws.validate(sn)

        if arg not in ("serialNumber", "alternateDeviceId",):
            raise ValueError(_(u"Invalid input for warranty check: %s") % sn)

        product = gsxws.Product(sn)
        wty     = product.warranty()
        model   = product.model()

        if device is None:
            # serialNumber may sometimes come back empty
            serial_number = wty.serialNumber or sn
            device = Device(sn=serial_number)

        from servo.lib.utils import empty

        if empty(device.notes):
            device.notes = wty.notes or ''
            device.notes += wty.csNotes or ''

        device.has_onsite       = product.has_onsite
        device.is_vintage       = product.is_vintage
        device.description      = product.description
        device.fmip_active      = product.fmip_is_active

        device.slug             = slugify(device.description)
        device.configuration    = wty.configDescription or ''
        device.purchase_country = wty.purchaseCountry or ''

        device.config_code      = model.configCode
        device.product_line     = model.productLine.replace(" ", "")
        device.parts_and_labor_covered = product.parts_and_labor_covered

        device.sla_description      = wty.slaGroupDescription or ''
        device.contract_start_date  = wty.contractCoverageStartDate
        device.contract_end_date    = wty.contractCoverageEndDate
        device.onsite_start_date    = wty.onsiteStartDate
        device.onsite_end_date      = wty.onsiteEndDate

        if wty.estimatedPurchaseDate:
            device.purchased_on = wty.estimatedPurchaseDate

        device.image_url         = wty.imageURL or ''
        device.manual_url        = wty.manualURL or ''
        device.exploded_view_url = wty.explodedViewURL or ''

        if wty.warrantyStatus:
            device.set_wty_status(wty.warrantyStatus)

        if product.is_ios:
            ad = device.get_activation()
            device.imei = ad.imeiNumber or ''
            device.unlocked = product.is_unlocked(ad)
            device.applied_activation_policy = ad.appliedActivationDetails or ''
            device.initial_activation_policy = ad.initialActivationPolicyDetails or ''
            device.next_tether_policy = ad.nextTetherPolicyDetails or ''

        cache.set(cache_key, device)

        return device

    def is_mac(self):
        """
        Returns True if this is a Mac
        """
        p = gsxws.Product(self.sn)
        p.description = self.description
        return p.is_mac

    def is_ios(self):
        """
        Returns True if this is an iOS device
        """
        p = gsxws.Product(self.sn)
        p.description = self.description
        return p.is_ios

    def update_gsx_details(self):
        Device.from_gsx(self.sn, self)
        self.save()

    def get_image_url(self):
        url = 'https://static.servoapp.com/images/products/%s.jpg' % self.slug
        return self.image_url or url

    def get_photo(self):
        try:
            return self.photo.url
        except ValueError:
            return self.get_image_url()
            
    def get_fmip_status(self):
        """
        Returns the translated FMiP status
        """
        return _('Active') if self.fmip_active else _('Inactive')

    def get_coverage_details(self):
        details = []
        if self.sla_description:
            details.append(_(u'SLA Group: %s') % self.sla_description)
        if self.has_onsite:
            details.append(_('This unit is eligible for Onsite Service.'))
        if self.parts_and_labor_covered:
            details.append(_('Parts and Labor are covered.'))

        return details

    @property
    def can_create_carryin(self):
        if self.description == "Non-Serialized Products":
            # Non-serialized products may have more than one repair
            return True

        return self.repair_set.filter(completed_at=None).count() < 1

    def get_accessories(self, order):
        return self.accessory_set.filter(order=order).values_list('name', flat=True)

    def get_activation(self):
        return gsxws.Product(self.sn).activation()

    def get_diagnostics(self, user):
        """
        Fetch GSX iOS or Repair diagnostics based on device type
        """
        GsxAccount.default(user)
        from gsxws.diagnostics import Diagnostics

        if len(self.imei):
            diags = Diagnostics(alternateDeviceId=self.imei)
        else:
            diags = Diagnostics(serialNumber=self.sn)

        diags.shipTo = user.location.gsx_shipto
        return diags.fetch()

    def get_warranty(self):
        return gsxws.Product(self.sn).warranty()

    def get_repairs(self):
        return gsxws.Product(self.sn).repairs()

    def get_parts(self):
        """
        Returns GSX parts for a product with this device's serialNumber
        """
        results = {}
        cache_key = "%s_parts" % self.sn

        for p in gsxws.Product(self.sn).parts():
            product = Product.from_gsx(p)
            results[product.code] = product

        cache.set_many(results)
        cache.set(cache_key, results.values())

        return results.values()

    def import_parts(self):
        pass

    def save(self, *args, **kwargs):
        if self.sn:
            self.sn = self.sn.strip().upper()

        self.description = self.description.strip()
        if self.slug is None:
            self.slug = slugify(self.description)

        return super(Device, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('devices-view_device', args=[self.product_line,
                                                    self.slug,
                                                    self.pk])

    def get_purchase_country(self):
        """
        Returns device's purchase country
        can be 2-letter code (from checkin) or
        full country name (from GSX)
        """
        from django_countries import countries

        if len(self.purchase_country) > 2:
            return self.purchase_country

        return countries.countries.get(self.purchase_country, '')

    def run_test(self, test_id, request):
        GsxAccount.default(request.user)
        diags = diagnostics.Diagnostics(self.sn)
        diags.shipTo = request.user.location.gsx_shipto
        diags.diagnosticSuiteId = test_id
        return diags.run_test()

    def fetch_tests(self, request):
        GsxAccount.default(request.user)
        diags = diagnostics.Diagnostics(self.sn)
        diags.shipTo = request.user.location.gsx_shipto
        return diags.fetch_suites()

    def get_gsx_repairs(self):
        """
        Returns this device's GSX repairs, if any
        """
        device = gsxws.Product(self.get_sn())
        results = []

        for i, p in enumerate(device.repairs()):
            d = {'purchaseOrderNumber': p.purchaseOrderNumber}
            d['repairConfirmationNumber'] = p.repairConfirmationNumber
            d['createdOn'] = p.createdOn
            d['customerName'] = p.customerName.encode('utf-8')
            d['repairStatus'] = p.repairStatus
            results.append(d)
            
        return results

    def __unicode__(self):
        return '%s (%s)' % (self.description, self.sn)

    class Meta:
        app_label = "servo"
        get_latest_by = "id"


@receiver(post_save, sender=Device)
def device_saved(sender, instance, created, **kwargs):
    # make sure we have this tag and product category
    if created:
        DeviceGroup.objects.get_or_create(title=instance.description)

    #  Update order descriptions
    for o in instance.order_set.all():
        o.description = instance.description
        o.save()
