# -*- coding: utf-8 -*-

import re
import gsxws

from django.db.models import Q
from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django.http import QueryDict, HttpResponseRedirect

from servo.lib.utils import paginate
from servo.models import (Note, Device, Product, 
                         GsxAccount, PurchaseOrder, Order,
                         ServiceOrderItem, Customer, ProductCategory,)


def search_gsx(request, what, param, query):
    """
    The first phase of a GSX search. Sets up the GSX connection.
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

    return render(request, "devices/search_gsx.html", locals())


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
            except gsxws.GsxError as e:
                return render(request, error_template, {'message': e})

            product = Product.from_gsx(partinfo)
            cache.set(query, product)
            results.append(product)

        if param == "serialNumber":
            try:
                dev = Device.from_gsx(query)
                products = dev.get_parts()
                return render(request, "devices/parts.html", locals())
            except gsxws.GsxError as message:
                return render(request, "search/results/gsx_error.html", locals())

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
            except gsxws.GsxError as e:
                return render(request, "search/results/gsx_notfound.html")

        elif param == "dispatchId":
            # ... with a repair confirmation number
            repair = gsxws.Repair(number=query)
            try:
                results = repair.lookup()
            except gsxws.GsxError as message:
                return render(request, error_template, locals())

    return render(request, "devices/search_gsx_%s.html" % what, locals())



def products(request):
    """
    Searches our local inventory
    """
    query = request.GET.get("q")
    request.session['search_query'] = query

    results = Product.objects.filter(
        Q(code__icontains=query) | Q(title__icontains=query) | Q(eee_code__icontains=query)
    )

    page = request.GET.get("page")
    products = paginate(results, page, 50)

    title = _(u'Search results for "%s"') % query
    group = ProductCategory(title=_('All'), slug='all')

    return render(request, 'products/search.html', locals())


def orders(request):
    """
    Searches local service orders
    """
    query = request.GET.get("q")

    if not query or len(query) < 3:
        messages.error(request, _('Search query is too short'))
        return redirect(reverse('orders-index'))

    request.session['search_query'] = query

    # Redirect Order ID:s to the order
    try:
        order = Order.objects.get(code__iexact=query)
        return redirect(order)
    except Order.DoesNotExist:
        pass

    orders = Order.objects.filter(
        Q(code=query) | Q(devices__sn__contains=query) |
        Q(customer__fullname__icontains=query) |
        Q(customer__phone__contains=query) |
        Q(repair__confirmation=query) |
        Q(repair__reference=query)
    )

    data = {
        'title': _('Orders'),
        'subtitle': _(u'%d results for "%s"') % (orders.count(), query)
    }

    page = request.GET.get('page')
    data['orders'] = paginate(orders.distinct(), page, 100)

    return render(request, "orders/index.html", data)


def customers(request):
    """
    Searches for customers from "spotlight"
    """
    query = request.GET.get("q")
    kind = request.GET.get('kind')
    request.session['search_query'] = query

    customers = Customer.objects.filter(
        Q(fullname__icontains=query) | Q(email__icontains=query) | Q(phone__contains=query)
    )

    if kind == 'company':
        customers = customers.filter(is_company=True)

    if kind == 'contact':
        customers = customers.filter(is_company=False)

    title = _('%d results for "%s"') % (customers.count(), query)

    return render(request, "customers/search.html", locals())


def devices(request):
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


def notes(request):
    """
    Searches for local notes
    """
    query = request.GET.get("q")
    request.session['search_query'] = query

    results = Note.objects.filter(body__icontains=query).order_by('-created_at')
    title = _(u'%d search results for "%s"') % (results.count(), query,)
    notes = paginate(results, request.GET.get('page'), 10)

    return render(request, "notes/search.html", locals())


def spotlight(request):
    """
    Searches for anything and redirects to the "closest" result view.
    GSX searches are done separately.

    To give good results, we must first "classify" the search query.
    Some strings are easy to classify:
    - serial numbers, repair confirmations, part numbers
    Others, not so much:
    - customer names, notes
    """
    hint = request.GET.get('hint')

    if hint == 'orders':
        return orders(request)

    if hint == 'customers':
        return customers(request)

    if hint == 'devices':
        return devices(request)

    if hint == 'notes':
        return notes(request)

    if hint == 'products':
        return products(request)

    messages.error(request, _('No search query provided'))
    return redirect(reverse('orders-index'))
