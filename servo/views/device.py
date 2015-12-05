# -*- coding: utf-8 -*-

import gsxws

from django.db.models import Q
from django.contrib import messages

from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404

from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page

from servo.lib.utils import paginate
from servo.models import Device, Order, Product, GsxAccount, ServiceOrderItem
from servo.forms.devices import DeviceForm, DeviceUploadForm, DeviceSearchForm


def model_from_slug(product_line, model=None):
    """
    Returns product description for model slug or models dict for
    the specified product line
    """
    if not cache.get("slugmap"):
        slugmap = {}  # Map model slug to corresponding product description
        product_lines = gsxws.products.models()

        for k, v in product_lines.items():
            d = {}
            for p in v['models']:
                slug = slugify(p)
                d[slug] = p

            slugmap[k] = d

        cache.set("slugmap", slugmap)

    models = cache.get("slugmap").get(product_line)

    if model is not None:
        return models.get(model)

    return models


def prep_list_view(request, product_line=None, model=None):
    """
    Prepares the basic device list view
    """
    title = _('Devices')
    search_hint = "devices"
    all_devices = Device.objects.all()
    product_lines = gsxws.products.models()

    if product_line is None:
        product_line = product_lines.keys()[0]

    models = model_from_slug(product_line)

    if model is None:
        model = models.keys()[0]
        title = product_lines[product_line]['name']
    else:
        title = models.get(model)

    if product_line == "OTHER":
        all_devices = all_devices.filter(product_line=product_line)
    else:
        all_devices = all_devices.filter(slug=model)

    page = request.GET.get('page')
    devices = paginate(all_devices, page, 50)
    return locals()


def prep_detail_view(request, pk, product_line=None, model=None):
    if pk is None:
        device = Device()
    else:
        device = get_object_or_404(Device, pk=pk)

    data = prep_list_view(request, product_line, model)

    data['device'] = device
    data['title']  = device.description

    return data


def index(request, product_line=None, model=None):
    if request.session.get('return_to'):
        del(request.session['return_to'])

    data = prep_list_view(request, product_line, model)

    if data['all_devices'].count() > 0:
        return redirect(data['all_devices'].latest())

    return render(request, "devices/index.html", data)


def delete_device(request, product_line, model, pk):
    dev = get_object_or_404(Device, pk=pk)

    if request.method == 'POST':
        from django.db.models import ProtectedError
        try:
            dev.delete()
            messages.success(request, _("Device deleted"))
        except ProtectedError:
            messages.error(request, _("Cannot delete device with GSX repairs"))
            return redirect(dev)

        return redirect(index)

    data = {'action': request.path}
    data['device'] = dev

    return render(request, "devices/remove.html", data)


def edit_device(request, pk=None, product_line=None, model=None):
    """
    Edits an existing device or adds a new one
    """
    device = Device()
    device.sn = request.GET.get('sn', '')

    if product_line is not None:
        device.product_line = product_line

    if model is not None:
        device.product_line = product_line
        device.description = model_from_slug(product_line, model)

    if pk is not None:
        device = get_object_or_404(Device, pk=pk)

    form = DeviceForm(instance=device)

    if request.method == "POST":

        form = DeviceForm(request.POST, request.FILES, instance=device)

        if form.is_valid():
            device = form.save()
            messages.success(request, _(u"%s saved") % device.description)
            device.add_tags(request.POST.getlist('tag'))

            return redirect(view_device,
                            pk=device.pk,
                            product_line=device.product_line,
                            model=device.slug)

    data = prep_detail_view(request, pk, product_line, model)
    data['form'] = form

    return render(request, 'devices/form.html', data)


def view_device(request, pk, product_line=None, model=None):
    data = prep_detail_view(request, pk, product_line, model)
    return render(request, "devices/view.html", data)


def find(request):
    """
    Searching for device from devices/find
    """
    title = _("Device search")
    form = DeviceSearchForm()
    results = Device.objects.none()

    if request.method == 'POST':
        form = DeviceSearchForm(request.POST)
        if form.is_valid():
            fdata = form.cleaned_data
            results = Device.objects.all()

            if fdata.get("product_line"):
                results = results.filter(product_line__in=fdata['product_line'])
            if fdata.get("warranty_status"):
                results = results.filter(warranty_status__in=fdata['warranty_status'])
            if fdata.get("description"):
                results = results.filter(description__icontains=fdata['description'])
            if fdata.get("sn"):
                results = results.filter(sn__icontains=fdata['sn'])
            if fdata.get("date_start"):
                results = results.filter(created_at__range=[fdata['date_start'],
                                         fdata['date_end']])

    page = request.GET.get("page")
    devices = paginate(results, page, 100)
    
    return render(request, "devices/find.html", locals())


#@cache_page(60*5)
def parts(request, pk, order_id, queue_id):
    """
    Lists available parts for this device/order
    taking into account the order's queues GSX Sold-To
    and the Location's corresponding GSX account
    """
    from decimal import InvalidOperation
    
    device = get_object_or_404(Device, pk=pk)
    order = device.order_set.get(pk=order_id)

    try:
        # remember the right GSX account
        act = GsxAccount.default(request.user, order.queue)
        request.session['gsx_account'] = act.pk
        products = device.get_parts()
    except gsxws.GsxError as message:
        return render(request, "search/results/gsx_error.html", locals())
    except AttributeError:
        message = _('Invalid serial number for parts lookup')
        return render(request, "search/results/gsx_error.html", locals())
    except InvalidOperation:
        message = _('Error calculating prices. Please check your system settings.')
        return render(request, "search/results/gsx_error.html", locals())

    return render(request, "devices/parts.html", locals())


def model_parts(request, product_line=None, model=None):
    """
    Shows parts for this device model
    """
    data = prep_list_view(request, product_line, model)

    if cache.get("slugmap") and model:
        models = cache.get("slugmap")[product_line]
        data['what']        = "parts"
        data['param']       = "productName"
        data['query']       = models[model]
        data['products']    = Product.objects.filter(tags__tag=data['query'])

    return render(request, "devices/index.html", data)


def choose(request, order_id):
    """
    Choosing a device from within an SRO
    Does GSX lookup in case device is not found locally
    """
    context = {'order': order_id}

    if request.method == "POST":

        query = request.POST.get('q').upper()
        results = Device.objects.filter(Q(sn__iexact=query) | Q(imei=query))

        if len(results) < 1:
            try:
                current_order = request.session.get("current_order_id")
                current_order = Order.objects.get(pk=current_order)
                if current_order and current_order.queue:
                    GsxAccount.default(request.user, current_order.queue)
                else:
                    GsxAccount.default(request.user)
                    results = [Device.from_gsx(query)]
            except Exception as e:
                context['error'] = e
                return render(request, "devices/choose-error.html", context)

        context['results'] = results
        return render(request, "devices/choose-list.html", context)

    return render(request, "devices/choose.html", context)


def upload_devices(request):
    """
    User uploads device DB as tab-delimited CSV file
    SN  USERNAME    PASSWORD    NOTES
    """
    gsx_account = None
    form = DeviceUploadForm()

    if request.method == "POST":
        form = DeviceUploadForm(request.POST, request.FILES)

        if form.is_valid():
            i = 0
            df = form.cleaned_data['datafile'].read()

            if form.cleaned_data.get('do_warranty_check'):
                gsx_account = GsxAccount.default(request.user)

            for l in df.split("\r"):
                l = l.decode("latin-1").encode("utf-8")
                row = l.strip().split("\t")

                if gsx_account:
                    try:
                        device = Device.from_gsx(row[0])
                    except Exception as e:
                        messages.error(request, e)
                        break
                else:
                    device = Device.objects.get_or_create(sn=row[0])[0]

                try:
                    device.username = row[1]
                    device.password = row[2]
                    device.notes = row[3]
                except IndexError:
                    pass

                device.save()
                i += 1

                if form.cleaned_data.get("customer"):
                    customer = form.cleaned_data['customer']
                    customer.devices.add(device)

            messages.success(request, _("%d devices imported") % i)

            return redirect(index)

    data = {'form': form, 'action': request.path}
    return render(request, "devices/upload_devices.html", data)


def update_gsx_details(request, pk):
    """
    Updates devices GSX warranty details
    """
    device = get_object_or_404(Device, pk=pk)
    try:
        GsxAccount.default(request.user)
        device.update_gsx_details()
        messages.success(request, _("Warranty status updated successfully"))
    except Exception as e:
        messages.error(request, e)

    if request.session.get('return_to'):
        return redirect(request.session['return_to'])

    return redirect(device)


def get_info(request, pk):
    device = get_object_or_404(Device, pk=pk)
    return render(request, "devices/get_info.html", locals())


def search_gsx_repairs(request, pk):
    """
    Performs async GSX search for this device's GSX repairs
    """
    device = get_object_or_404(Device, pk=pk)
    
    try:
        GsxAccount.default(request.user)
        results = {'results': device.get_gsx_repairs()}
        return render(request, "devices/search_gsx_repairs.html", results)
    except gsxws.GsxError as message:
        return render(request, "search/results/gsx_error.html", locals())
