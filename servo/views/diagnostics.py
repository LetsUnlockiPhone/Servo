# -*- coding: utf-8 -*-
import gsxws

from django.db.models import Q
from django.contrib import messages

from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect, get_object_or_404


from servo.models import Device, Order, Product, GsxAccount, ServiceOrderItem


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


def run_test(request, device, test_id):
    device = get_object_or_404(Device, pk=device)
    try:
        device.run_test(test_id, request)
    except Exception as e:
        messages.error(request, e)
    

def select_test(request, pk):
    """
    Fetch test suite selector
    """
    error = None
    device = get_object_or_404(Device, pk=pk)

    try:
        tests = device.fetch_tests(request)
    except Exception as e:
        error = e

    return render(request, "diagnostics/select_test.html", locals())


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
            except gsxws.GsxError as e:
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
