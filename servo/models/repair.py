# -*- coding: utf-8 -*-

import json
import gsxws
import os.path

from gsxws.repairs import SymptomIssue

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxLengthValidator

from servo import defaults
from servo.lib.utils import cache_getset
from servo.models.common import GsxAccount
from servo.models import Queue, Order, Device, Product
from servo.models.order import ServiceOrderItem
from servo.models.parts import ServicePart
from servo.models.purchases import PurchaseOrder, PurchaseOrderItem


class Checklist(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("title"),
        default=_('New Checklist')
    )
    queues = models.ManyToManyField(
        Queue,
        blank=True,
        verbose_name=_("queue")
    )

    enabled = models.BooleanField(default=True, verbose_name=_("Enabled"))

    def get_admin_url(self):
        return reverse('admin-edit_checklist', args=[self.pk])

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = "servo"
        ordering = ("title",)
        verbose_name = _('Checklist')
        verbose_name_plural = _('Checklists')


class ChecklistItem(models.Model):
    checklist = models.ForeignKey(Checklist)
    title = models.CharField(max_length=255, verbose_name=_("Task"))
    description = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Description')
    )
    """
    reported = models.BooleanField(
        default=True,
        verbose_name=_("Reported"),
        help_text=_('Report this result to the customer')
    )
    """

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = "servo"


class ChecklistItemValue(models.Model):
    order = models.ForeignKey(Order)
    item = models.ForeignKey(ChecklistItem)

    checked_at = models.DateTimeField(auto_now_add=True)
    checked_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        app_label = "servo"


class ActiveManager(models.Manager):
    """
    GSX repairs that have been submitted, and not marked complete
    """
    def active(self, **kwargs):
        return self.filter(completed_at=None, **kwargs).exclude(submitted_at=None)


class Repair(models.Model):
    """
    Proxies service order data between our internal
    service orders and GSX repairs
    """
    order  = models.ForeignKey(Order, editable=False, on_delete=models.PROTECT)
    device = models.ForeignKey(Device, editable=False, on_delete=models.PROTECT)
    parts  = models.ManyToManyField(ServiceOrderItem, through=ServicePart)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False,
        on_delete=models.PROTECT,
        related_name="created_repairs"
    )

    tech_id = models.CharField(
        default='',
        blank=True,
        max_length=15,
        verbose_name=_(u'Technician')
    )
    unit_received_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_(u'Unit Received')
    )
    submitted_at = models.DateTimeField(null=True, editable=False)
    completed_at = models.DateTimeField(null=True, editable=False)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        editable=False,
        on_delete=models.PROTECT,
        related_name="completed_repairs"
    )
    request_review = models.BooleanField(
        default=False,
        help_text=_("Repair should be reviewed by Apple before confirmation")
    )
    confirmation = models.CharField(max_length=10, default='', editable=False)
    reference = models.CharField(
        blank=True,
        default='',
        max_length=16,
        verbose_name=_("Reference")
    )

    symptom = models.TextField()
    diagnosis = models.TextField()
    notes = models.TextField(
        blank=True,
        default='',
        validators=[MaxLengthValidator(800)],
        help_text=_("Notes are mandatory when requesting review.")
    )
    status = models.CharField(default='', editable=False, max_length=128)
    attachment = models.FileField(
        upload_to='repairs',
        null=True,
        blank=True,
        help_text=_('Choose files to be sent with the repair creation request')
    )
    repair_number = models.CharField(default='', max_length=12, editable=False)
    mark_complete = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_("mark complete"),
        help_text=_("Requires replacement serial number")
    )
    replacement_sn = models.CharField(
        blank=True,
        default='',
        max_length=18,
        verbose_name=_("New serial number"),
        help_text=_("Serial Number of replacement part")
    )
    # the account through which this repair was submitted
    gsx_account = models.ForeignKey(
        GsxAccount,
        editable=False,
        on_delete=models.PROTECT
    )

    repair_type = models.CharField(
        max_length=2,
        default="CA",
        editable=False,
        choices=gsxws.REPAIR_TYPES
    )

    component_data = models.TextField(default='', editable=False)
    consumer_law = models.NullBooleanField(
        default=None,
        help_text=_('Repair is eligible for consumer law coverage')
    )
    acplus = models.NullBooleanField(
        default=None,
        verbose_name=_('AppleCare+'),
        help_text=_('Repair is covered by AppleCare+')
    )

    symptom_code = models.CharField(max_length=7, default='')
    issue_code = models.CharField(max_length=7, default='')
    objects = models.Manager()
    active = ActiveManager()

    def is_submitted(self):
        return self.submitted_at is not None

    def get_symptom_code_choices(self):
        """
        Returns the possible symptom codes for the current serial number
        """
        # @fixme: what if it's someone else ordering the part?
        self.gsx_account.connect(self.created_by)
        ckey = 'symptom_codes-%s' % self.device.sn
        si = SymptomIssue(serialNumber=self.device.sn)
        return cache_getset(ckey, si.fetch)

    def get_issue_code_choices(self):
        """
        Returns the possible issue codes for the current symptom code
        """
        # @fixme: what if it's someone else ordering the part?
        self.gsx_account.connect(self.created_by)
        ckey = 'issue_codes-%s' % self.symptom_code
        si = SymptomIssue(reportedSymptomCode=self.symptom_code)
        return cache_getset(ckey, si.fetch)

    @property
    def has_cl_parts(self):
        """
        Returns true if this repair contains Consumer Law parts
        """
        return self.servicepart_set.filter(coverage_status='VW').exists()

    @property
    def can_mark_complete(self):
        """
        Returns true if this repair can be marked complete after submitting
        """
        parts = self.servicepart_set.all()
        if len(parts) > 1: return False
        replacements = [p for p in parts if p.is_replacement()]
        return len(replacements) == 1

    @classmethod
    def create_from_gsx(cls, confirmation, order, device, user):
        """
        Creates a new Repair for order with confirmation number
        """
        try:
            repair = cls.objects.get(confirmation=confirmation)
            msg = {'repair': repair.confirmation, 'order': repair.order}
            raise ValueError(_('Repair %(repair)s already exists for order %(order)s') % msg)
        except cls.DoesNotExist:
            pass

        repair = cls(order=order, created_by=user)
        repair.device = device
        repair.confirmation = confirmation
        repair.gsx_account = GsxAccount.default(user, order.queue)
        repair.submitted_at = timezone.now() # RepairDetails doesn't have this!
        repair.save()

        try:
            repair.get_details()
            repair.update_status(user)
        except gsxws.GsxError as e:
            if e.code == 'RPR.LKP.01': # repair not found
                repair.delete()
                raise ValueError(_('Repair %s not found in GSX') % confirmation)

        return repair

    def create_purchase_order(self):
        # Create local purchase order
        po = PurchaseOrder(supplier="Apple", created_by=self.created_by)
        po.location = self.created_by.get_location()
        po.reference = self.reference
        po.sales_order = self.order
        po.save()
        return po

    def warranty_status(self):
        """
        Gets warranty status for this device and these parts
        """
        self.connect_gsx(self.created_by)
        product = gsxws.Product(self.device.sn)
        parts = [(p.code, p.comptia_code,) for p in self.order.get_parts()]
        return product.warranty(parts, self.get_received_date())

    def is_open(self):
        return self.completed_at is None

    def get_products(self):
        """
        Returns the Service Order Items in this Repair
        """
        return [x.order_item for x in self.servicepart_set.all()]

    def get_number(self, user=None):
        return self.confirmation or _("New GSX Repair")

    def set_parts(self, parts):
        """
        Resets this Repair's part listing
        """
        ServicePart.objects.filter(repair=self).delete()
        for p in parts:
            part = ServicePart.from_soi(self, p)
            part.save()

    def add_part(self, order_item, user):
        """
        Adds this Order Item as a part to this GSX repair
        """
        self.connect_gsx(user)
        gsx_rep = self.get_gsx_repair()

        part = ServicePart.from_soi(self, order_item)
        order_line = part.get_repair_order_line()

        gsx_rep.update({'orderLines': [order_line]})
        part.order(user)

        return part

    def add_gsx_part(self, part):
        """
        Adds a part that has been added manually in GSX web UI
        """
        # part has been added to the order, but not the GSX repair
        try:
            oi = self.order.products.get(code=part.partNumber)
        except ServiceOrderItem.DoesNotExist:
            new_part = ServicePart(part_number=part.partNumber)
            try:
                p = Product.objects.get(code=part.partNumber)
            except Product.DoesNotExist:
                p = Product.from_gsx(new_part.lookup())
                p.save()

            oi = self.order.add_product(p, 1, self.created_by)

        oi.comptia_code = part.comptiaCode or ''
        oi.comptia_modifier = part.comptiaModifier or ''
        oi.save()

        sp = ServicePart.from_soi(self, oi)
        sp.set_part_details(part)

        sp.order(self.created_by)
        sp.save()

    def submit(self, customer_data):
        """
        Creates a new GSX repair and all the documentation that goes along with it
        """
        if len(self.parts.all()) < 1:
            raise ValueError(_("Please add some parts to the repair"))

        if not self.order.queue:
            raise ValueError(_("Order has not been assigned to a queue"))


        repair_data = self.to_gsx()

        if self.repair_type == "CA":
            gsx_repair = gsxws.CarryInRepair(**repair_data)
        if self.repair_type == "ON":
            gsx_repair = gsxws.IndirectOnsiteRepair(**repair_data)

        customer_data['regionCode'] = self.gsx_account.region
        gsx_repair.customerAddress = gsxws.Customer(**customer_data)

        if self.component_data:
            ccd = []
            cd = json.loads(self.component_data)
            for k, v in cd.items():
                ccd.append(gsxws.ComponentCheck(component=k, serialNumber=v))

            gsx_repair.componentCheckDetails = ccd

        parts = [p.get_repair_order_line() for p in self.servicepart_set.all()]
        gsx_repair.orderLines = parts

        # Submit the GSX repair request
        result = gsx_repair.create()

        po = self.create_purchase_order()

        for p in self.servicepart_set.all():
            p.purchase_order = po
            p.created_by = self.created_by
            p.save()

            poi = PurchaseOrderItem.from_soi(po, p.order_item, self.created_by)
            poi.save()

        confirmation = result.confirmationNumber
        self.confirmation = confirmation
        self.submitted_at = timezone.now()

        po.confirmation = confirmation
        po.submit(self.created_by)

        self.save()

        msg = _(u"GSX repair %s created") % confirmation
        self.order.notify("gsx_repair_created", msg, self.created_by)

        if repair_data.get("markCompleteFlag") is True:
            self.close(self.created_by)

    def get_gsx_repair(self):
        return gsxws.CarryInRepair(self.confirmation)

    def get_unit_received(self):
        """
        Returns (as a tuple) the GSX-compatible date and time of
        when this unit was received
        """
        import locale
        langs = gsxws.get_format('en_XXX')
        ts = self.unit_received_at
        loc = locale.getlocale()
        # reset locale to get correct AM/PM value
        locale.setlocale(locale.LC_TIME, None)
        result = ts.strftime(langs['df']), ts.strftime(langs['tf'])
        locale.setlocale(locale.LC_TIME, loc)
        return result

    def get_received_date(self):
        return self.get_unit_received()[0]

    def to_gsx(self):
        """
        Returns this Repair as a GSX-compatible dict
        """
        data = {'serialNumber': self.device.sn}
        data['notes'] = self.notes
        data['symptom'] = self.symptom
        data['poNumber'] = self.reference
        data['diagnosis'] = self.diagnosis
        data['shipTo'] = self.gsx_account.ship_to

        data['reportedSymptomCode'] = self.symptom_code
        data['reportedIssueCode'] = self.issue_code

        # checkIfOutOfWarrantyCoverage
        if self.tech_id:
            data['diagnosedByTechId'] = self.tech_id

        ts = self.get_unit_received()
        data['unitReceivedDate'] = ts[0]
        data['unitReceivedTime'] = ts[1]

        if self.attachment:
            data['fileData'] = self.attachment
            data['fileName'] = os.path.basename(self.attachment.name)

        if self.mark_complete:
            data['markCompleteFlag'] = self.mark_complete
            data['replacementSerialNumber'] = self.replacement_sn

        data['requestReviewByApple'] = self.request_review

        if self.consumer_law is not None:
            data['consumerLawEligible'] = self.consumer_law

        if self.acplus is not None:
            data['acPlusFlag'] = self.acplus

        return data

    def has_serialized_parts(self):
        """
        Checks if this Repair has any serialized parts
        """
        count = self.parts.filter(servicepart__order_item__product__is_serialized=True).count()
        return count > 0

    def check_components(self):
        """
        Runs GSX component check for this repair's parts
        """
        l = gsxws.Lookup(serialNumber=self.device.sn)
        l.repairStrategy = self.repair_type
        l.shipTo = self.gsx_account.ship_to
        parts = []

        for i in self.servicepart_set.all():
            part = gsxws.ServicePart(i.part_number)
            part.symptomCode = i.comptia_code
            parts.append(part)

        try:
            r = l.component_check(parts)
        except gsxws.GsxError as e:
            if e.code == "COMP.LKP.004":
                return # Symptom Code not required for Replacement and Other category parts.
            raise e

        if r.componentDetails is None:
            return

        if len(self.component_data) < 1:
            d = {}
            for i in r.componentDetails:
                f = i.componentCode
                d[f] = i.componentDescription

            self.component_data = json.dumps(d)

        return self.component_data

    def connect_gsx(self, user=None):
        """
        Initialize the GSX session with the right credentials.
        User can also be different from the one who initially created the repair.
        """
        account = user or self.created_by
        self.gsx_account.connect(account)

    def set_status(self, new_status, user):
        """
        Sets the current status of this repair to new_status
        and notifies the corresponding Service Order
        """
        if not new_status == self.status:
            self.status = new_status
            self.save()
            self.order.notify("repair_status_changed", self.status, user)

    def get_status(self):
        return self.status if len(self.status) else _('No status')

    def update_status(self, user):
        repair = self.get_gsx_repair()
        status = repair.status().repairStatus
        self.set_status(status, user)

        return self.status

    def get_details(self):
        repair = self.get_gsx_repair()
        details = repair.details()

        if isinstance(details.partsInfo, dict):
            details.partsInfo = [details.partsInfo]

        self.update_details(details)
        return details

    def get_return_label(self, part):
        self.get_details()
        part = self.servicepart_set.get(pk=part)
        return part.get_return_label()

    def update_details(self, details):
        """
        Updates what local info we have about this particular GSX repair
        """
        part_list = list(self.servicepart_set.all().order_by('id'))

        for i, p in enumerate(details.partsInfo):
            try:
                part = part_list[i]
                part.set_part_details(p)
                part.save()
            except IndexError: # part added in GSX web ui...
                self.add_gsx_part(p)
            except AttributeError: # some missing attribute in set_part_details()
                pass

    def get_replacement_sn(self):
        """
        Try to guess replacement part's SN
        """
        oi = self.order.serviceorderitem_set.filter(
            product__is_serialized=True,
            product__part_type="REPLACEMENT"
        )

        try:
            return oi[0].sn
        except IndexError:
            pass

    def complete(self, user):
        """
        Marks this repair as being complete
        """
        self.completed_at = timezone.now()
        self.completed_by = user
        self.save()

        queue = self.order.queue
        if queue.status_repair_completed:
            status = queue.status_repair_completed
            self.order.set_status(status, user)

    def get_sn_update_parts(self):
        """
        Returns parts eligible for SN update
        """
        return self.servicepart_set.exclude(return_code='GPR')

    def close(self, user):
        """
        Marks this GSX repair as complete
        """
        self.connect_gsx(user)
        repair = self.get_gsx_repair()

        try:
            # Update part serial numbers
            [part.update_sn() for part in self.get_sn_update_parts()]
            repair.mark_complete()
        except gsxws.GsxError as e:
            """
            Valid GSX errors are:
            'ACT.BIN.01': Repair # provided is not valid. Please enter a valid repair #.
            'RPR.LKP.01': No Repair found matching search criteria.
            'RPR.LKP.010': No Repair found matching the search criteria.
            'RPR.COM.030': Cannot mark repair as complete for Unit $1. Repair is not open.
            'RPR.COM.036': Repair for Unit $1 is already marked as complete.
            'RPR.COM.019': This repair cannot be updated.
            'RPR.LKP.16': This Repair Cannot be Updated.Repair is not Open.
            'RPR.COM.136': Repair $1 cannot be marked complete as the Warranty
            Claims Certification Form status is either Declined or Hold.
            'ENT.UPL.022': 'Confirmation # $1 does not exist.'
            """
            errorlist = (
                'ACT.BIN.01',
                'RPR.LKP.01',
                'RPR.LKP.010',
                'RPR.COM.030',
                'RPR.COM.036',
                'RPR.COM.019',
                'RPR.LKP.16',
                'RPR.COM.136',
                'ENT.UPL.022',
            )

            if e.code not in errorlist:
                raise e

        status = repair.status()
        self.set_status(status.repairStatus, user)

        self.complete(user)

    def duplicate(self, user):
        """
        Makes a copy of this GSX Repair
        """
        new_rep = Repair(order=self.order, created_by=user, device=self.device)
        new_rep.repair_type = self.repair_type
        new_rep.tech_id = self.tech_id
        new_rep.symptom = self.symptom
        new_rep.diagnosis = self.diagnosis
        new_rep.notes = self.notes
        new_rep.reference = self.reference
        new_rep.request_review = self.request_review
        new_rep.mark_complete = self.mark_complete
        new_rep.unit_received_at = self.unit_received_at
        new_rep.attachment = self.attachment
        new_rep.gsx_account = self.gsx_account

        new_rep.save()
        new_rep.set_parts(self.order.get_parts())

        return new_rep

    def get_absolute_url(self):
        if self.submitted_at is None:
            return reverse('repairs-edit_repair', args=[self.order.pk, self.pk])
        return reverse('repairs-view_repair', args=[self.order.pk, self.pk])

    def __unicode__(self):
        if self.pk is not None:
            return _("Repair %d") % self.pk

    class Meta:
        app_label = "servo"
        get_latest_by = "created_at"
