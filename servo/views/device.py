# -*- coding: utf-8 -*-

import gsxws

from django.db.models import Q
from django.contrib import messages

from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404

from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from servo.models import Device, Order, Product, GsxAccount, ServiceOrderItem
from servo.forms.devices import DeviceForm, DeviceUploadForm, DeviceSearchForm


class RepairDiagnosticResults:
    pass


class DiagnosticResults(object):
    def __init__(self, diags):
        if not diags.diagnosticTestData:
            raise gsxws.GsxError('Missing diagnostic data')

        self.diags = dict(result={}, profile={}, report={})

        for r in diags.diagnosticTestData.testResult.result:
            self.diags['result'][r.name] = r.value

        for r in diags.diagnosticProfileData.profile.unit.key:
            self.diags['profile'][r.name] = r.value

        for r in diags.diagnosticProfileData.report.reportData.key:
            self.diags['report'][r.name] = r.value

    def __iter__(self):
        return iter(self.diags)


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
    title = _('Devices')
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
    paginator = Paginator(all_devices, 50)

    try:
        devices = paginator.page(page)
    except PageNotAnInteger:
        devices = paginator.page(1)
    except EmptyPage:
        devices = paginator.page(paginator.num_pages)

    return locals()


def prep_detail_view(request, pk, product_line=None, model=None):
    if pk is None:
        device = Device()
    else:
        device = Device.objects.get(pk=pk)

    data = prep_list_view(request, product_line, model)

    data['device'] = device
    data['title'] = device.description

    return data


def index(request, product_line=None, model=None):
    if request.session.get('return_to'):
        del(request.session['return_to'])

    data = prep_list_view(request, product_line, model)

    if data['all_devices'].count() > 0:
        return redirect(data['all_devices'].latest())

    return render(request, "devices/index.html", data)


def delete_device(request, product_line, model, pk):
    dev = Device.objects.get(pk=pk)

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
        device = Device.objects.get(pk=pk)

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


def diagnostics(request, pk):
    """
    Fetches MRI diagnostics or initiates iOS diags from GSX
    """
    device = get_object_or_404(Device, pk=pk)

    if request.GET.get('a') == 'init':
        if request.method == 'POST':
            from gsxws import diagnostics
            order = request.POST.get('order')
            order = device.order_set.get(pk=order)
            email = request.POST.get('email')
            diag = diagnostics.Diagnostics(serialNumber=device.sn)
            diag.emailAddress = email
            diag.shipTo = order.location.gsx_shipto

            try:
                GsxAccount.default(request.user)
                res = diag.initiate()
                msg = _('Diagnostics initiated - diags://%s') % res
                order.notify("init_diags", msg, request.user)
                messages.success(request, msg)
            except gsxws.GsxError, e:
                messages.error(request, e)

            return redirect(order)

        order = request.GET.get('order')
        order = device.order_set.get(pk=order)
        customer = order.customer
        url = request.path
        return render(request, "devices/diagnostic_init.html", locals())

    if request.GET.get('a') == 'get':
        try:
            diagnostics = device.get_diagnostics(request.user)
            if device.is_ios():
                diagnostics = DiagnosticResults(diagnostics)
                return render(request, "devices/diagnostic_ios.html", locals())
            return render(request, "devices/diagnostic_results.html", locals())
        except gsxws.GsxError as e:
            return render(request, "devices/diagnostic_error.html", {'error': e})

    return render(request, "devices/diagnostics.html", locals())


def get_gsx_search_results(request, what, param, query):
    """
    The second phase of a GSX search.
    There should be an active GSX session open at this stage.
    """
    data    = {}
    results = []
    query   = query.upper()
    device  = Device(sn=query)
    error_template = "search/results/gsx_error.html"

    # @TODO: this isn't a GSX search. Move it somewhere else.
    if what == "orders":
        try:
            if param == 'serialNumber':
                device = Device.objects.get(sn__exact=query)
            if param == 'alternateDeviceId':
                device = Device.objects.get(imei__exact=query)
        except (Device.DoesNotExist, ValueError,):
            return render(request, "search/results/gsx_notfound.html")

        orders = device.order_set.all()
        return render(request, "orders/list.html", locals())

    if what == "warranty":
        # Update wty info if been here before
        try:
            device = Device.objects.get(sn__exact=query)
            device.update_gsx_details()
        except Exception:
            try:
                device = Device.from_gsx(query)
            except Exception as e:
                return render(request, error_template, {'message': e})

        results.append(device)

        # maybe it's a device we've already replaced...
        try:
            soi = ServiceOrderItem.objects.get(sn__iexact=query)
            results[0].repeat_service = soi.order
        except ServiceOrderItem.DoesNotExist:
            pass

    if what == "parts":
        # looking for parts
        if param == "partNumber":
            # ... with a part number
            part = gsxws.Part(partNumber=query)

            try:
                partinfo = part.lookup()
            except gsxws.GsxError, e:
                return render(request, error_template, {'message': e})

            product = Product.from_gsx(partinfo)
            cache.set(query, product)
            results.append(product)

        if param == "serialNumber":
            # ... with a serial number
            try:
                results = device.get_parts()
                data['device'] = device
            except Exception as e:
                return render(request, error_template, {'message': e})

        if param == "productName":
            product = gsxws.Product(productName=query)
            parts = product.parts()
            for p in parts:
                results.append(Product.from_gsx(p))

    if what == "repairs":
        # Looking for GSX repairs
        if param == "serialNumber":
            # ... with a serial number
            try:
                device = gsxws.Product(query)
                #results = device.repairs()
                # @TODO: move the encoding hack to py-gsxws
                for i, p in enumerate(device.repairs()):
                    d = {'purchaseOrderNumber': p.purchaseOrderNumber}
                    d['repairConfirmationNumber'] = p.repairConfirmationNumber
                    d['createdOn'] = p.createdOn
                    d['customerName'] = p.customerName.encode('utf-8')
                    d['repairStatus'] = p.repairStatus
                    results.append(d)
            except gsxws.GsxError, e:
                return render(request, "search/results/gsx_notfound.html")

        elif param == "dispatchId":
            # ... with a repair confirmation number
            repair = gsxws.Repair(number=query)
            try:
                results = repair.lookup()
            except gsxws.GsxError as message:
                return render(request, error_template, locals())

    return render(request, "devices/search_gsx_%s.html" % what, locals())


def search_gsx(request, what, param, query):
    """
    The first phase of a GSX search
    """
    title = _(u'Search results for "%s"') % query

    try:
        act = request.session.get("gsx_account")
        act = None
        if act is None:
            GsxAccount.default(user=request.user)
        else:
            act.connect(request.user)
    except gsxws.GsxError as message:
        return render(request, "devices/search_gsx_error.html", locals())

    if request.is_ajax():
        if what == "parts":
            try:
                dev = Device.from_gsx(query)
                products = dev.get_parts()
                return render(request, "devices/parts.html", locals())
            except gsxws.GsxError as message:
                return render(request, "search/results/gsx_error.html", locals())

        return get_gsx_search_results(request, what, param, query)

    return render(request, "devices/search_gsx.html", locals())


def search(request):
    """
    Searching for devices from the main navbar
    """
    query = request.GET.get("q", '').strip()
    request.session['search_query'] = query

    query = query.upper()
    valid_arg = gsxws.validate(query)

    if valid_arg in ('serialNumber', 'alternateDeviceId',):
        return redirect(search_gsx, "warranty", valid_arg, query)

    devices = Device.objects.filter(
        Q(sn__icontains=query) | Q(description__icontains=query)
    )

    title = _(u'Devices matching "%s"') % query

    return render(request, "devices/search.html", locals())


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

    paginator = Paginator(results, 100)
    page = request.GET.get("page")

    try:
        devices = paginator.page(page)
    except PageNotAnInteger:
        devices = paginator.page(1)
    except EmptyPage:
        devices = paginator.page(paginator.num_pages)

    return render(request, "devices/find.html", locals())


#@cache_page(60*5)
def parts(request, pk, order_id, queue_id):
    """
    Lists available parts for this device/order
    taking into account the order's queues GSX Sold-To
    and the Location's corresponding GSX account
    """
    from decimal import InvalidOperation
    
    device = Device.objects.get(pk=pk)
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
