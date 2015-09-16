# -*- coding: utf-8 -*-

import re
import gsxws

from django.db.models import Q
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from django.http import QueryDict, HttpResponseRedirect

from servo.models.note import Note
from servo.models.wiki import Article
from servo.models.device import Device
from servo.models.product import Product
from servo.models.common import GsxAccount
from servo.models.purchases import PurchaseOrder
from servo.models.order import Order, ServiceOrderItem


def results_redirect(view, data):
    q = QueryDict('', mutable=True)
    q['q'] = data['query']
    query_str = q.urlencode()
    url = reverse(view, args=[data['what']])
    return HttpResponseRedirect("%s?%s" % (url, query_str))


def prepare_result_view(request):

    query = request.GET.get('q')

    data = {'title': _('Search results for "%s"' % query)}

    data['gsx_type'] = gsxws.validate(query.upper())
    data['query'] = query
    data['tag_id'] = None
    data['cat_id'] = None  # Product category
    data['group'] = 'all'  # customer group

    return data, query


def list_gsx(request, what="warranty"):
    data, query = prepare_result_view(request)
    data['what'] = what
    return render(request, "search/results/gsx.html", data)


def search_gsx(request, what, arg, value):
    if request.is_ajax():

        if what == "parts" and value != "None":
            results = []
            GsxAccount.default(user=request.user)

            try:
                product = gsxws.Product(productName=value)
                parts = product.parts()
                for p in parts:
                    results.append(Product.from_gsx(p))
            except gsxws.GsxError, e:
                data = {'message': e}
                return render(request, "search/results/gsx_error.html", data)

            data = {'results': results}

        return render(request, "search/results/gsx_%s.html" % what, data)

    data = {arg: value}
    return render(request, "search/gsx_results.html", data)


def view_gsx_results(request, what="warranty"):
    """
    Searches for something from GSX. Defaults to warranty lookup.
    GSX search strings are always UPPERCASE.
    """
    results = list()
    data, query = prepare_result_view(request)
    query = query.upper()

    error_template = "search/results/gsx_error.html"

    if data['gsx_type'] == "dispatchId":
        what = "repairs"

    if data['gsx_type'] == "partNumber":
        what = "parts"

    data['what'] = what
    gsx_type = data['gsx_type']

    try:
        if request.session.get("current_queue"):
            queue = request.session['current_queue']
            GsxAccount.default(request.user, queue)
        else:
            GsxAccount.default(request.user)
    except gsxws.GsxError, e:
        error = {'message': e}
        return render(request, error_template, error)

    if gsx_type == "serialNumber" or "alternateDeviceId":
        try:
            device = Device.objects.get(sn=query)
        except Device.DoesNotExist:
            device = Device(sn=query)

    if what == "warranty":
        if cache.get(query):
            result = cache.get(query)
        else:
            try:
                result = Device.from_gsx(query)
            except gsxws.GsxError, e:
                error = {'message': e}
                return render(request, error_template, error)

        if re.match(r'iPhone', result.description):
            result.activation = device.get_activation()

        results.append(result)

    if what == "parts":
        # looking for parts
        if gsx_type == "partNumber":
            # ... with a part number
            part = gsxws.Part(partNumber=query)

            try:
                partinfo = part.lookup()
            except gsxws.GsxError, e:
                error = {'message': e}
                return render(request, error_template, error)

            product = Product.from_gsx(partinfo)
            cache.set(query, product)
            results.append(product)
        else:
            # ... with a serial number
            try:
                results = device.get_parts()
                data['device'] = device
            except Exception, e:
                error = {'message': e}
                return render(request, error_template, error)

    if what == "repairs":
        # Looking for GSX repairs
        if gsx_type == "serialNumber":
            # ... with a serial number
            try:
                device = gsxws.Product(query)
                results = device.repairs()
            except gsxws.GsxError, e:
                return render(request, "search/results/gsx_notfound.html")

        elif gsx_type == "dispatchId":
            # ... with a repair confirmation number
            repair = gsxws.Repair(number=query)
            try:
                results = repair.lookup()
            except gsxws.GsxError, e:
                error = {'message': e}
                return render(request, error_template, error)

    if what == "repair_details":
        repair = gsxws.Repair(number=query)
        results = repair.details()
        return render(request, "search/results/gsx_repair_details.html", results)

    # Cache the results for quicker access later
    cache.set('%s-%s' % (what, query), results)
    data['results'] = results

    return render(request, "search/results/gsx_%s.html" % what, data)


def list_products(request):
    data, query = prepare_result_view(request)
    data['products'] = Product.objects.filter(
        Q(code__icontains=query) | Q(title__icontains=query)
    )

    return render(request, "search/results/products.html", data)


def list_notes(request):
    data, query = prepare_result_view(request)
    data['notes'] = Note.objects.filter(body__icontains=query)
    return render(request, "search/results/notes.html", data)


def spotlight(request):
    """
    Searches for anything and redirects to the "closest" result view.
    GSX searches are done separately.
    """
    data, query = prepare_result_view(request)
    data['what'] = "warranty"

    if Order.objects.filter(customer__name__icontains=query).exists():
        return list_orders(request)

    if data['gsx_type'] == "serialNumber":
        try:
            device = Device.objects.get(sn=query)
            return redirect(device)
        except Device.DoesNotExist:
            return results_redirect("search-gsx", data)

    data['parts'] = ServiceOrderItem.objects.filter(sn__icontains=query)

    if gsxws.validate(query, "dispatchId"):
        try:
            po = PurchaseOrder.objects.get(confirmation=query)
            data['orders'] = [po.sales_order]
        except PurchaseOrder.DoesNotExist:
            pass

    data['products'] = Product.objects.filter(
        Q(code__icontains=query) | Q(title__icontains=query)
    )

    data['articles'] = Article.objects.filter(content__contains=query)

    return render(request, "search/spotlight.html", data)
