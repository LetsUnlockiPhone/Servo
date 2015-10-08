# -*- coding: utf-8 -*-

from django import forms
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.forms.models import inlineformset_factory
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from servo.forms.invoices import *
from servo.models import Order, Invoice, Payment, PurchaseOrder


def invoices(request):
    """
    Lists invoices, optionally with a search filter
    """
    from datetime import timedelta
    from django.db.models import Sum

    data = {'title': _("Invoices")}
    now = timezone.now()

    start_date, end_date = now - timedelta(days=30), now
    initial = {'start_date': start_date, 'end_date': end_date}

    invoices = Invoice.objects.filter(created_at__range=(start_date, end_date))
    form = InvoiceSearchForm(initial=initial)

    if request.method == 'POST':
        invoices = Invoice.objects.all()
        form = InvoiceSearchForm(request.POST, initial=initial)

        if form.is_valid():
            fdata = form.cleaned_data
            if fdata.get('state') == 'OPEN':
                invoices = invoices.filter(paid_at=None)
            if fdata.get('state') == 'PAID':
                invoices = invoices.exclude(paid_at=None)

            payment_method = fdata.get('payment_method')
            if len(payment_method):
                invoices = invoices.filter(payment__method=payment_method)

            start_date = fdata.get('start_date', start_date)
            end_date = fdata.get('end_date', end_date)
            invoices = invoices.filter(created_at__range=(start_date, end_date))

            if fdata.get('status_isnot'):
                invoices = invoices.exclude(order__status__status=fdata['status_isnot'])

            if fdata.get('customer_name'):
                invoices = invoices.filter(customer_name__icontains=fdata['customer_name'])

            if fdata.get('service_order'):
                invoices = invoices.filter(order__code__exact=fdata['service_order'])

    page = request.GET.get('page')
    data['total'] = invoices.aggregate(Sum('total_net'))
    data['total_paid'] = invoices.exclude(paid_at=None).aggregate(Sum('total_net'))
    pos = PurchaseOrder.objects.filter(created_at__range=[start_date, end_date])
    data['total_purchases'] = pos.aggregate(Sum('total'))

    paginator = Paginator(invoices, 50)

    try:
        invoices = paginator.page(page)
    except PageNotAnInteger:
        invoices = paginator.page(1)
    except EmptyPage:
        invoices = paginator.page(paginator.num_pages)

    data['form'] = form
    data['invoices'] = invoices

    return render(request, "invoices/index.html", data)


def gsx_invoices(request):
    pass


def print_invoice(request, pk):
    from servo.models import Configuration

    invoice = get_object_or_404(Invoice, pk=pk)
    template = invoice.order.get_print_template("receipt")

    title = _("Receipt #%d") % invoice.pk
    conf = Configuration.conf()
    order = invoice.order

    return render(request, template, locals())


def view_invoice(request, pk):
    title = _("Invoice %s") % pk
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, "invoices/view_invoice.html", locals())


@permission_required('servo.change_order')
def create_invoice(request, order_id=None, numbers=None):
    """
    Dispatches Sales Order
    """
    order = get_object_or_404(Order, pk=order_id)
    title = _(u'Dispatch Order %s') % order.code
    products = order.products.filter(dispatched=False)

    initial = {
        'order': order,
        'products': products,
        'total_tax': order.total_tax(),
        'total_net': order.net_total(),
        'total_gross': order.gross_total(),
    }

    total_margin = order.total_margin()

    invoice = Invoice(order=order)
    invoice.created_by = request.user
    invoice.customer = order.customer
    invoice.total_margin = total_margin

    if order.customer:
        customer = order.customer
        initial['customer_name'] = customer.name
        initial['customer_phone'] = customer.phone
        initial['customer_email'] = customer.email
        initial['customer_address'] = customer.street_address
    else:
        initial['customer_name'] = _(u'Walk-In Customer')

    form = InvoiceForm(initial=initial, instance=invoice, prefix='invoice')

    PaymentFormset = inlineformset_factory(Invoice, Payment, extra=1, form=PaymentForm, exclude=[])
    initial = [{'amount': order.gross_total, 'created_by': request.user}]
    formset = PaymentFormset(initial=initial, prefix='payment')

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice, prefix='invoice')
        if form.is_valid():
            invoice = form.save()
            formset = PaymentFormset(request.POST, instance=invoice, prefix='payment')

            if formset.is_valid():
                payments = formset.save()
            else:
                messages.error(request, formset.errors)
                return render(request, "orders/dispatch.html", locals())

            products = request.POST.getlist('items')

            try:
                order.dispatch(invoice=invoice, products=products)
                messages.success(request, _(u'Order %s dispatched') % order.code)
            except Exception as e:
                messages.error(request, e)

            if form.cleaned_data.get('close'):
                order.close(request.user)
                messages.success(request, _(u'Order %s closed') % order.code)

            return redirect(order)
        else:
            messages.error(request, form.errors)

    return render(request, "orders/dispatch.html", locals())


@permission_required('servo.change_order')
def add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    payment = Payment(invoice=invoice)
    payment.created_by = request.user
    payment.amount = request.POST.get('amount')
    payment.save()
