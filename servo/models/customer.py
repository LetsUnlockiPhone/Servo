# -*- coding: utf-8 -*-

import phonenumbers
from django.db import models
from django.conf import settings

from mptt.managers import TreeManager
from django.core.validators import validate_email
from django.template.defaultfilters import slugify
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext_lazy as _

from pytz import country_names

from servo import defaults
from servo.models import Tag
from servo.models.device import Device


class CustomerGroup(models.Model):
    name = models.CharField(
        unique=True,
        max_length=255,
        default=_('New Group'),
        verbose_name=_('name')
    )

    slug = models.SlugField(editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(CustomerGroup, self).save()

    def __unicode__(self):
        return self.name

    class Meta:
        get_latest_by = 'id'
        app_label = "servo"
        ordering = ('id',)


class Customer(MPTTModel):
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='contacts',
        verbose_name=_('company'),
        limit_choices_to={'is_company': True}
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('name'),
        default=_('New Customer')
    )
    fullname = models.CharField(
        default='',
        editable=False,
        max_length=255
    )
    phone = models.CharField(
        default='',
        blank=True,
        max_length=32,
        verbose_name=_('phone')
    )
    email = models.EmailField(
        blank=True,
        default='',
        verbose_name=_('email')
    )
    street_address = models.CharField(
        blank=True,
        default='',
        max_length=128,
        verbose_name=_('address')
    )
    zip_code = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_('ZIP Code')
    )
    city = models.CharField(
        blank=True,
        default='',
        max_length=32,
        verbose_name=_('city')
    )
    COUNTRY_CHOICES = [(k, country_names[k]) for k in sorted(country_names)]
    country = models.CharField(
        blank=True,
        max_length=2,
        verbose_name=_('Country'),
        default=defaults.country,
        choices=COUNTRY_CHOICES
    )
    photo = models.ImageField(
        null=True,
        blank=True,
        upload_to="photos",
        verbose_name=_('photo')
    )

    groups = models.ManyToManyField(
        CustomerGroup,
        blank=True,
        verbose_name=_('Groups')
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name=_('tags'),
        limit_choices_to={'type': 'customer'}
    )

    notes = models.TextField(
        blank=True,
        default='',
        verbose_name=_("notes")
    )

    devices = models.ManyToManyField(
        Device,
        blank=True,
        editable=False,
        verbose_name=_("devices")
    )

    created_at = models.DateTimeField(auto_now=True)
    is_company = models.BooleanField(
        default=False,
        verbose_name=_("company"),
        help_text=_('Companies can contain contacts')
    )

    objects = TreeManager()

    def get_contacts(self):
        return self.get_descendants(include_self=False)

    def get_phone(self):
        return phonenumbers.parse(self.phone, self.country)

    def get_standard_phone(self):
        n = self.get_phone()
        fmt = phonenumbers.PhoneNumberFormat.E164
        return phonenumbers.format_number(n, fmt)

    def get_international_phone(self):
        n = self.get_phone()
        fmt = phonenumbers.PhoneNumberFormat.INTERNATIONAL
        return phonenumbers.format_number(n, fmt)

    def get_national_phone(self):
        n = self.get_phone()
        fmt = phonenumbers.PhoneNumberFormat.NATIONAL
        return phonenumbers.format_number(n, fmt)

    def get_company_name(self):
        """Since we don't really have a "company" field in Servo,
        climb up the parent tree and return a concated name
        """
        return ', '.join([i for i in self.get_parents()])

    def valid_email(self):
        """
        Returns email address or raises ValidationError
        """
        try:
            validate_email(self.email)
            return self.email
        except Exception:
            pass

    def get_email_address(self):
        return '%s <%s>' % (self.name, self.email)

    def get_closest_prop(self, prop):
        """
        Gets the 'closest' value of a property
        """
        ancestors = self.get_ancestors(ascending=True, include_self=True)
        for a in ancestors:
            attr = getattr(a, prop)
            if attr:
                return attr

    def gsx_address(self, location):
        """
        Returns a dictionary that's compatibly with GSX's Address datatype
        """
        out = dict()

        out['country'] = location.get_country()
        out['city'] = self.get_closest_prop('city') or location.city
        out['zipCode'] = self.get_closest_prop('zip_code') or location.zip_code
        out['primaryPhone'] = self.get_closest_prop('phone') or location.phone
        out['emailAddress'] = self.get_closest_prop('email') or u'refused@apple.com'
        out['addressLine1'] = self.get_closest_prop('street_address') or location.address

        try:
            (out['firstName'], out['lastName']) = self.name.split(" ", 1)
        except Exception:
            out['firstName'], out['lastName'] = self.name, self.name

        return out

    def get_property(self, key):
        """
        Returns the value of a specific property
        """
        result = None
        ci = ContactInfo.objects.filter(customer=self)
        for i in ci:
            if i.key == key:
                result = i.value

        return result

    @property
    def firstname(self):
        return self.name.split(" ")[0]

    @property
    def lastname(self):
        return self.name.split(" ")[1].rstrip(',')

    def get_fullname(self):
        """
        Gets the entire name tree for this customer
        """
        title = list()

        for a in self.get_ancestors():
            title.append(a.name)

        if len(title) < 1:
            return self.name

        return self.name + " - " + str(", ").join(title)

    def fullprops(self):
        """
        Get the combined view of all the properties for this customer
        """
        props = {}
        for r in self.contactinfo_set.all():
            props[r.key] = r.value

        return props

    def get_group(self):
        try:
            return self.groups.latest('id').slug
        except CustomerGroup.DoesNotExist:
            return "all"

    def get_absolute_url(self):
        return "/customers/%s/%d/" % (self.get_group(), self.pk)

    def get_icon(self):
        return 'icon-briefcase' if self.is_company else 'icon-user'

    def save(self, *args, **kwargs):
        self.zip_code = self.zip_code.replace(' ', '')

        super(Customer, self).save(*args, **kwargs)
        fn = self.get_fullname()

        if self.fullname != fn:
            self.fullname = fn
            self.save()

            for o in self.orders.all():
                o.customer_name = fn
                o.save()

    class Meta:
        app_label = "servo"

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name


class ContactInfo(models.Model):
    customer = models.ForeignKey(Customer)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        app_label = 'servo'
        # Only allow a field once per customer
        unique_together = ('customer', 'key',)
