# -*- coding: utf-8 -*-

import gsxws
import logging

from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required

from servo.models import Order, GsxAccount, Repair, ServicePart
from servo.forms import GsxCustomerForm, GsxRepairForm, GsxComponentForm, ImportForm


class RepairDetails(object):
    def __init__(self, confirmation):
        repair = gsxws.Repair(confirmation).details()
        self.dispatch_id = repair.dispatchId
        self.po_number = repair.purchaseOrderNumber
        self.cs_code = repair.csCode
        self.tracking_number = repair.deliveryTrackingNumber
        self.notes = repair.notes
        self.status = repair.repairStatus
        self.status_description = repair.coverageStatusDescription
        self.parts = repair.partsInfo


@permission_required("servo.change_order")
def register_return(request, part_id):
    part = get_object_or_404(ServicePart, pk=part_id)
    try:
        part.register_for_return(request.user)
        messages.success(request, _(u"Part %s updated") % part.order_item.code)
    except Exception as e:
        messages.error(request, e)

    return redirect(part.repair.order)


@permission_required("servo.change_repair")
def import_repair(request, order_pk, device_pk):
    from servo.models import Device
    order = get_object_or_404(Order, pk=order_pk)
    device = get_object_or_404(Device, pk=device_pk)

    action = request.path
    form = ImportForm()

    if request.method == 'POST':
        form = ImportForm(request.POST)
        if form.is_valid():
            confirmation = form.cleaned_data['confirmation']
            try:
                repair = Repair.create_from_gsx(confirmation,
                                                order,
                                                device,
                                                request.user)
                messages.success(request, _('GSX repair %s imported successfully' % confirmation))
                return redirect(repair)
            except Exception as e:
                messages.error(request, e)
                return redirect(order)

    return render(request, "repairs/import_repair.html", locals())

    
@permission_required("servo.change_order")
def return_label(request, repair, part):
    """
    Returns the return label PDF for this repair and part
    """
    repair = get_object_or_404(Repair, pk=repair)

    try:
        repair.connect_gsx(request.user)
        label_data = repair.get_return_label(part)
        return HttpResponse(label_data, content_type="application/pdf")
    except gsxws.GsxError as e:
        messages.error(request, e)
        return redirect(repair.order)


@permission_required("servo.change_repair")
def add_part(request, repair, part):
    """
    Adds this part to this GSX repair
    """
    rep = get_object_or_404(Repair, pk=repair)
    soi = rep.order.serviceorderitem_set.get(pk=part)

    if request.method == "POST":
        try:
            part = rep.add_part(soi, request.user)
            data = {'part': part.part_number, 'repair': rep.confirmation}
            msg = _("Part %(part)s added to repair %(repair)s") % data
            messages.success(request, msg)
        except gsxws.GsxError, e:
            messages.error(request, e)

        return redirect(rep.order)

    context = {'item': soi}
    context['repair'] = rep
    context['action'] = request.path

    return render(request, "repairs/add_part.html", context)


def remove_part(request, repair, part):
    rep = get_object_or_404(Repair, pk=repair)
    part = get_object_or_404(ServicePart, pk=part)

    if request.method == "POST":

        rep.connect_gsx(request.user)
        gsx_rep = rep.get_gsx_repair()
        orderline = part.get_repair_order_line()
        orderline.toDelete = True
        orderline.orderLineNumber = part.line_number

        try:
            gsx_rep.update({'orderLines': [orderline]})
            data = {'part': part.code, 'repair': rep.confirmation}
            msg = _(u"Part %(part)s removed from %(repair)s") % data
            messages.success(request, msg)
        except gsxws.GsxError, e:
            messages.error(request, e)

        return redirect(rep.order)

    data = {'action': request.path}
    return render(request, "repairs/delete_part.html", data)


def delete_repair(request, repair_id):
    repair = get_object_or_404(Repair, pk=repair_id)
    if repair.submitted_at:
        messages.error(request, _('Submitted repairs cannot be deleted'))
        return redirect(repair.order)

    if request.method == 'POST':
        order = repair.order
        repair.delete()
        messages.success(request, _('GSX repair deleted'))
        return redirect(order)

    context = {'action': request.path}
    return render(request, 'repairs/delete_repair.html', context)


def check_parts_warranty(request, repair):
    """
    Checks this (new) repair warranty status
    with the included device and parts
    """
    repair = get_object_or_404(Repair, pk=repair)
    parts = repair.order.get_parts()

    try:
        wty = repair.warranty_status()
        wty_parts = wty.parts
        repair.acplus = wty.acPlusFlag
    except Exception as e:
        return render(request, 'search/results/gsx_error.html', {'message': e})

    try:
        for k, v in enumerate(parts):
            try:
                parts[k].warranty_status = wty_parts[k].partWarranty
            except TypeError:
                parts[k].warranty_status = _('Unknown')
    except KeyError:
        parts[0].warranty_status = wty_parts.partWarranty

    context = {'parts': parts}
    context['checked_parts'] = [p.pk for p in repair.parts.all()]
    return render(request, 'repairs/check_parts.html', context)


def prep_edit_view(request, repair, order=None, device=None):
    """
    Prepares edit view for GSX repair
    """
    context = {'order': order}

    if repair.submitted_at:
        raise ValueError(_("Submitted repairs cannot be edited"))

    if not order.has_parts:
        raise ValueError(_("Please add some parts before creating repair"))

    if not order.customer:
        raise ValueError(_("Cannot create GSX repair without valid customer data"))
    
    customer = order.customer.gsx_address(request.user.location)
    customer_form = GsxCustomerForm(initial=customer)

    context['repair'] = repair
    context['customer'] = customer
    context['title'] = repair.get_number()
    context['customer_form'] = customer_form
    context['device'] = device or repair.device
    context['repair_form'] = GsxRepairForm(instance=repair)

    if len(repair.component_data):
        context['component_form'] = GsxComponentForm(components=repair.component_data)

    return context


def edit_repair(request, order_id, repair_id):
    """
    Edits existing (non-submitted) GSX repair
    """
    order  = get_object_or_404(Order, pk=order_id)
    repair = get_object_or_404(Repair, pk=repair_id)

    if request.GET.get('c'):
        repair.symptom_code = request.GET['c']
        repair.save()
        choices = repair.get_issue_code_choices()
        return render(request, "repairs/issue_code_menu.html", locals())

    repair.set_parts(order.get_parts())

    try:
        repair.connect_gsx(request.user)
        repair.check_components()
        data = prep_edit_view(request, repair, order)
    except (ValueError, gsxws.GsxError) as e:
        messages.error(request, e)
        return redirect(order)

    if request.method == "POST":
        try:
            data = save_repair(request, data)
            msg = _('GSX repair saved')
            if 'confirm' in request.POST.keys():
                repair.submit(data['customer_data'])
                msg = _(u"GSX repair %s created") % repair.confirmation
                messages.success(request, msg)
                return redirect("repairs-view_repair", order.pk, repair.pk)
            messages.success(request, msg)
            return redirect(order)
        except Exception as e:
            messages.error(request, e)

    return render(request, "orders/gsx_repair_form.html", data)


def save_repair(request, context):
    """
    Saves this GSX repair
    """
    repair = context['repair']
    customer = context['customer']

    if len(repair.component_data):
        component_form = GsxComponentForm(request.POST,
                                          components=repair.component_data)
        if component_form.is_valid():
            repair.component_data = component_form.json_data
        else:
            raise ValueError(_("Invalid component data"))

    customer_form = GsxCustomerForm(request.POST, initial=customer)
    repair_form = GsxRepairForm(request.POST, request.FILES, instance=repair)

    if customer_form.is_valid():
        context['customer_data'] = customer_form.cleaned_data
        if repair_form.is_valid():
            repair = repair_form.save(commit=False)
            repair.set_parts(repair_form.cleaned_data['parts'])
            repair.save()
        else:
            raise ValueError(repair_form.errors)
    else:
        raise ValueError(_("Invalid customer info"))

    context['repair_form'] = repair_form
    context['customer_form'] = customer_form

    return context


def create_repair(request, order_id, device_id, type):
    """
    Creates a GSX repair for the specified SRO and device
    and redirects to the repair's edit page.
    """
    from datetime import timedelta
    from django.utils import timezone
    
    order = get_object_or_404(Order, pk=order_id)
    device = order.devices.get(pk=device_id)

    repair = Repair(order=order, created_by=request.user, device=device)
    timediff = timezone.now() - order.created_at

    if timediff.seconds <= 3600:
        repair.unit_received_at = order.created_at - timedelta(hours=1)
    else:
        repair.unit_received_at = order.created_at

    repair.reference = request.user.gsx_poprefix + order.code

    try:
        repair.gsx_account = GsxAccount.default(request.user, order.queue)
    except Exception as e:
        messages.error(request, e)
        return redirect(order)

    repair.repair_type = type
    repair.tech_id = request.user.tech_id
    repair.save()

    return redirect(edit_repair, order.pk, repair.pk)


def repair_details(request, confirmation):
    """
    Returns GSX repair details for confirmation number
    """
    try:
        repair = RepairDetails(confirmation)
    except Exception as e:
        data = {'error': e}
        return render(request, "snippets/error_modal.html", data)
    
    data = {'repair': repair}

    if request.method == "POST":
        data = save_repair(request, data)

    return render(request, "repairs/get_details.html", data)


def copy_repair(request, pk):
    """
    Duplicates a local GSX repair
    """
    repair = get_object_or_404(Repair, pk=pk)
    new_repair = repair.duplicate(request.user)
    return redirect(edit_repair, new_repair.order_id, new_repair.pk)


def update_sn(request, pk, part):
    """
    Updates the parts serial number
    """
    part = get_object_or_404(ServicePart, pk=part)

    try:
        part.repair.connect_gsx(request.user)
        part.update_sn()
        msg = _(u'%s serial numbers updated') % part.part_number
        messages.success(request, msg)
    except Exception as e:
        messages.error(request, e)

    return redirect(part.repair.order)
