# -*- coding: utf-8 -*-
# Copyright (c) 2013, First Party Software
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
# SUCH DAMAGE.

from __future__ import absolute_import

from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse

from django.forms.models import modelform_factory
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from servo.models.note import Note
from servo.models.order import Order
from servo.models.common import Property
from servo.models.customer import Customer, CustomerGroup, ContactInfo

from servo.forms.customer import (CustomerForm,
                                  CustomerSearchForm,
                                  CustomerUploadForm)

GroupForm = modelform_factory(CustomerGroup, exclude=[])


def prepare_view(request, group='all'):

    title = _("Customers")

    customer_list = []
    all_customers = Customer.objects.all().order_by('name')
    customer_count = all_customers.count()

    if request.session.get("return_to"):
        del(request.session['return_to'])

    if request.method == 'POST':
        q = request.POST.get('query')
        if q is not None:
            try:
                (key, value) = q.split('=')
                # allow searching customers by arbitrary key/values
                customer_list = Customer.objects.filter(**{key: value.strip()})
            except Exception:
                customer_list = Customer.objects.filter(name__icontains=q)
    else:
        if group == 'all':
            customer_list = all_customers
        else:
            g = CustomerGroup.objects.get(slug=group)
            customer_list = all_customers.filter(groups=g)
            title = g.name

    page = request.GET.get('page')
    paginator = Paginator(customer_list, 40)

    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)

    groups = CustomerGroup.objects.all()

    return locals()


def index(request, group='all'):
    data = prepare_view(request, group)
    request.session['customer_query'] = None

    if data['customer_list']:
        customer = data['customer_list'][0]
        return redirect(view, pk=customer.pk, group=group)

    return render(request, "customers/index.html", data)


@permission_required("servo.change_order")
def add_order(request, customer_id, order_id):
    order = Order.objects.get(pk=order_id)
    customer = Customer.objects.get(pk=customer_id)
    order.customer = customer
    order.save()

    for d in order.devices.all():
        customer.devices.add(d)

    customer.save()
    messages.success(request, _('Customer added'))
    return redirect(order)


def notes(request, pk, note_id=None):
    from servo.forms.note import NoteForm
    customer = Customer.objects.get(pk=pk)
    form = NoteForm(initial={'recipient': customer.name})

    return render(request, "notes/form.html", {'form': form})


def view(request, pk, group='all'):
    try:
        c = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        messages.error(request, _('Customer not found'))
        return redirect(index)

    data = prepare_view(request, group)

    data['title'] = c.name
    data['orders'] = Order.objects.filter(
        customer__lft__gte=c.lft,
        customer__rght__lte=c.rght,
        customer__tree_id=c.tree_id
    )

    if c.email:
        data['notes'] = Note.objects.filter(recipient=c.email)

    data['customer'] = c
    request.session['return_to'] = request.path

    return render(request, 'customers/view.html', data)


@permission_required("servo.change_customer")
def edit_group(request, group='all'):
    if group == 'all':
        group = CustomerGroup()
    else:
        group = CustomerGroup.objects.get(slug=group)

    title = group.name
    form = GroupForm(instance=group)

    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            messages.success(request, _(u'%s saved') % group.name)
            return redirect(index, group.slug)
        messages.error(request, form.errors['name'][0])
        return redirect(index)

    return render(request, "customers/edit_group.html", locals())


@permission_required("servo.change_customer")
def delete_group(request, group):
    group = CustomerGroup.objects.get(slug=group)

    if request.method == "POST":
        group.delete()
        messages.success(request, _(u'%s deleted') % group.name)
        return redirect(index)

    return render(request, "customers/delete_group.html", locals())


@permission_required("servo.change_customer")
def edit(request, pk=None, parent_id=None, group='all'):

    data = prepare_view(request, group)

    customer = Customer()
    form = CustomerForm(instance=customer)

    if group != 'all':
        g = CustomerGroup.objects.get(slug=group)
        form.initial = {'groups': [g]}

    name = request.GET.get('name')

    if name:
        form = CustomerForm(initial={'name': name})

    if pk is not None:
        customer = Customer.objects.get(pk=pk)
        form = CustomerForm(instance=customer)

    if parent_id is not None:
        customer.parent = Customer.objects.get(pk=parent_id)
        form = CustomerForm(initial={'parent': parent_id})

    if request.method == 'POST':
        props = dict()
        keys = request.POST.getlist('keys')
        values = request.POST.getlist('values')

        form = CustomerForm(request.POST, request.FILES, instance=customer)

        if form.is_valid():
            ContactInfo.objects.filter(customer=customer).delete()

            for k, v in enumerate(values):
                if v != '':
                    key = keys[k]
                    props[key] = v

            if form.is_valid():
                try:
                    customer = form.save()
                except Exception as e:
                    messages.error(request, e)
                    return redirect(edit, group, pk)

                for k, v in props.items():
                    if v != '':
                        ContactInfo.objects.create(key=k, value=v, customer=customer)

                messages.success(request, _('Customer saved'))

                if request.session.get('return_to'):
                    return_to = request.session['return_to']
                    if hasattr(return_to, 'set_customer'):
                        return_to.set_customer(customer)
                    del request.session['return_to']
                    return redirect(return_to)

                return redirect(view, pk=customer.pk, group=group)

    data['form'] = form
    data['customer'] = customer
    data['title'] = customer.name
    data['fields'] = Property.objects.filter(type='customer')

    return render(request, 'customers/form.html', data)


@permission_required("servo.delete_customer")
def delete(request, pk=None, group='all'):

    customer = Customer.objects.get(pk=pk)

    if request.method == "POST":
        customer.delete()
        messages.success(request, _("Customer deleted"))
        return redirect(index, group=group)
    else:
        data = {'action': request.path, 'customer': customer}
        return render(request, "customers/remove.html", data)


@permission_required("servo.change_customer")
def merge(request, pk, target=None):
    """
    Merges customer PK with customer TARGET
    Re-links everything from customer PK to TARGET:
    - orders
    - devices
    - invoices
    Deletes the source customer
    """
    customer = Customer.objects.get(pk=pk)
    title = _('Merge %s with') % customer.name

    if request.method == 'POST':
        name = request.POST.get('name')
        results = Customer.objects.filter(name__icontains=name)
        return render(request, 'customers/results-merge.html', locals())

    if pk and target:
        target_customer = Customer.objects.get(pk=target)
        target_customer.orders.add(*customer.orders.all())
        target_customer.devices.add(*customer.devices.all())
        target_customer.note_set.add(*customer.note_set.all())
        target_customer.invoice_set.add(*customer.invoice_set.all())
        target_customer.save()
        customer.delete()
        messages.success(request, _('Customer records merged succesfully'))
        return redirect(target_customer)

    return render(request, "customers/merge.html", locals())


@permission_required("servo.change_customer")
def move(request, pk, new_parent=None):
    """
    Moves a customer under another customer
    """
    customer = Customer.objects.get(pk=pk)

    if new_parent is not None:
        if int(new_parent) == 0:
            new_parent = None
            msg = _(u"Customer %s moved to top level") % customer
        else:
            new_parent = Customer.objects.get(pk=new_parent)
            d = {'customer': customer, 'target': new_parent}
            msg = _(u"Customer %(customer)s moved to %(target)s") % d

        try:
            customer.move_to(new_parent)
            customer.save()  # To update fullname
            messages.success(request, msg)
        except Exception, e:
            messages.error(request, e)

        return redirect(customer)

    return render(request, "customers/move.html", locals())


def search(request):
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


def filter(request):
    """
    Search for customers by name
    May return JSON for ajax requests
    or a rendered list
    """
    import json
    from django.http import HttpResponse

    if request.method == "GET":
        results = list()
        query = request.GET.get("query")
        customers = Customer.objects.filter(fullname__icontains=query)

        for c in customers:
            results.append(u"%s <%s>" % (c.name, c.email))
            results.append(u"%s <%s>" % (c.name, c.phone))
    else:
        query = request.POST.get("name")
        results = Customer.objects.filter(fullname__icontains=query)
        data = {'results': results, 'id': request.POST['id']}

        return render(request, "customers/search-results.html", data)

    return HttpResponse(json.dumps(results), content_type="application/json")


def find(request):
    """
    Search from customer advanced search
    """
    results = list()
    request.session['customer_list'] = list()

    if request.method == 'POST':
        form = CustomerSearchForm(request.POST)

        if form.is_valid():
            d = form.cleaned_data
            checkin_start = d.pop('checked_in_start')
            checkin_end = d.pop('checked_in_end')

            if checkin_start and checkin_end:
                d['orders__created_at__range'] = [checkin_start.isoformat(), 
                                                  checkin_end.isoformat()]

            results = Customer.objects.filter(**d).distinct()
            request.session['customer_query'] = d
    else:
        form = CustomerSearchForm()

    title = _('Search for customers')

    page = request.GET.get('page')
    paginator = Paginator(results, 50)

    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)

    return render(request, "customers/find.html", locals())


def download(request, format='csv', group='all'):
    """
    Downloads all customers or search results
    """
    filename = 'customers'
    results = Customer.objects.all()
    query = request.session.get('customer_query')

    response = HttpResponse(content_type="text/plain; charset=utf-8")
    response['Content-Disposition'] = 'attachment; filename="%s.txt"' % filename
    response.write(u"ID\tNAME\tEMAIL\tPHONE\tADDRESS\tPOSTAL CODE\tCITY\tCOUNTRY\tNOTES\n")

    if group != 'all':
        results = results.filter(groups__slug=group)

    if query:
        results = Customer.objects.filter(**query).distinct()

    for c in results:
        row = u"%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (c.pk,
                                                         c.name,
                                                         c.email,
                                                         c.phone,
                                                         c.street_address,
                                                         c.zip_code,
                                                         c.city,
                                                         c.country,
                                                         c.notes,)
        response.write(row)

    return response


def create_message(request, pk):
    return redirect("servo.views.note.edit", customer=pk)


def upload(request, group='all'):

    action = request.path
    form = CustomerUploadForm()

    if request.method == 'POST':
        form = CustomerUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            messages.error(request, form.errors)
            return redirect(index)

        i, df = 0, form.cleaned_data['datafile'].read()

        for l in df.split("\r"):
            row = force_decode(l).strip().split("\t")

            if len(row) < 5:
                messages.error(request, _("Invalid upload data"))
                return redirect(index)

            if form.cleaned_data.get('skip_dups'):
                if Customer.objects.filter(email=row[1]).exists():
                    continue

            c = Customer(name=row[0], email=row[1])
            c.street_address = row[2]
            c.zip_code = row[3]
            c.city = row[4]
            c.notes = row[5]
            c.save()

            if group != 'all':
                g = CustomerGroup.objects.get(slug=group)
                c.groups.add(g)

            i += 1

        messages.success(request, _("%d customer(s) imported") % i)
        return redirect(index, group=group)

    return render(request, "customers/upload.html", locals())


def force_decode(s, codecs=['mac_roman', 'utf-8', 'latin-1']):
    for i in codecs:
        try:
            return s.decode(i)
        except UnicodeDecodeError:
            pass
