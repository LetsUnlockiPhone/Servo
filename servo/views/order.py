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

import json

from gsxws.core import GsxError
from django.http import QueryDict

from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse

from django.db import DatabaseError

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from django.shortcuts import render, redirect, get_object_or_404

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from servo.models.order import *
from servo.forms.orders import *

from servo.models import Note, User, Device, Customer
from servo.models.common import (Tag,
                                 Configuration,
                                 FlaggedItem,
                                 GsxAccount,)
from servo.models.repair import (Checklist,
                                 ChecklistItem,
                                 Repair,
                                 ChecklistItemValue,)


def prepare_list_view(request, args):
    """
    Lists service orders matching specified criteria
    """
    data = {'title': _("Orders")}

    form = OrderSearchForm(args)
    form.fields['location'].queryset = request.user.locations

    if request.session.get("current_queue"):
        del(request.session['current_queue'])

    if request.session.get("return_to"):
        del(request.session['return_to'])

    if request.user.customer:
        orders = Order.objects.filter(customer=request.user.customer)
    else:
        orders = Order.objects.filter(location__in=request.user.locations.all())

    if args.get("state"):
        orders = orders.filter(state__in=args.getlist("state"))

    start_date = args.get("start_date")
    if start_date:
        end_date = args.get('end_date') or timezone.now()
        orders = orders.filter(created_at__range=[start_date, end_date])

    if args.get("assigned_to"):
        users = args.getlist("assigned_to")
        orders = orders.filter(user__in=users)

    if args.get("followed_by"):
        users = args.getlist("followed_by")
        orders = orders.filter(followed_by__in=users)

    if args.get("created_by"):
        users = args.getlist("created_by")
        orders = orders.filter(created_by__in=users)

    if args.get("customer"):
        customer = int(args['customer'][0])
        if customer == 0:
            orders = orders.filter(customer__pk=None)
        else:
            orders = orders.filter(customer__tree_id=customer)

    if args.get("spec"):
        spec = args['spec'][0]
        if spec is "None":
            orders = orders.filter(devices=None)
        else:
            orders = orders.filter(devices__slug=spec)

    if args.get("device"):
        orders = orders.filter(devices__pk=args['device'])

    if args.get("queue"):
        queue = args.getlist("queue")
        orders = orders.filter(queue__in=queue)

    if args.get("checkin_location"):
        ci_location = args.getlist("checkin_location")
        orders = orders.filter(checkin_location__in=ci_location)

    if args.get("location"):
        location = args.getlist("location")
        orders = orders.filter(location__in=location)

    if args.get("label"):
        orders = orders.filter(tags__in=args.getlist("label"))

    if args.get("status"):
        status = args.getlist("status")

        if args['status'][0] == 'None':
            orders = orders.filter(status__pk=None)
        else:
            orders = orders.filter(status__status__in=status)

    if args.get("color"):
        color = args.getlist("color")
        now = timezone.now()

        if "grey" in color:
            orders = orders.filter(status=None)
        if "green" in color:
            orders = orders.filter(status_limit_green__gte=now)
        if "yellow" in color:
            orders = orders.filter(status_limit_yellow__gte=now,
                                   status_limit_green__lte=now)
        if "red" in color:
            orders = orders.filter(status_limit_yellow__lte=now)

    page = request.GET.get("page")
    paginator = Paginator(orders.distinct(), 100)

    try:
        order_pages = paginator.page(page)
    except PageNotAnInteger:
        order_pages = paginator.page(1)
    except EmptyPage:
        order_pages = paginator.page(paginator.num_pages)

    data['form'] = form
    data['queryset'] = orders
    data['orders'] = order_pages
    data['subtitle'] = _("%d search results") % orders.count()

    # @FIXME!!! how to handle this with jsonserializer???
    #request.session['order_queryset'] = orders

    return data


def prepare_detail_view(request, pk):
    """
    Prepares the view for whenever we're dealing with a specific order
    """
    order = get_object_or_404(Order, pk=pk)

    request.session['current_order_id'] = None
    request.session['current_order_code'] = None
    request.session['current_order_customer'] = None

    title = _(u'Order %s') % order.code
    priorities = Queue.PRIORITIES
    followers = order.followed_by.all()
    locations = Location.objects.filter(enabled=True)
    queues = request.user.queues.all()
    users = order.get_available_users(request.user)

    # wrap the customer in a list for easier recursetree
    if order.customer is not None:
        customer = order.customer.get_ancestors(include_self=True)
        title = u'%s | %s' % (title, order.customer.name)
    else:
        customer = []

    statuses = []
    checklists = []

    if order.queue is not None:
        checklists = Checklist.objects.filter(queues=order.queue)
        statuses = order.queue.queuestatus_set.all()

    if order.is_editable:
        request.session['current_order_id'] = order.pk
        request.session['current_order_code'] = order.code
        request.session['return_to'] = order.get_absolute_url()
        if order.customer:
            request.session['current_order_customer'] = order.customer.pk

    return locals()


@permission_required("servo.change_order")
def close(request, pk):
    """
    Closes this Service Order
    """
    order = Order.objects.get(pk=pk)

    if request.method == 'POST':
        try:
            order.close(request.user)
        except Exception as e:
            messages.error(request, e)
            return redirect(order)

        if request.session.get("current_order_id"):
            del(request.session['current_order_id'])
            del(request.session['current_order_code'])
            del(request.session['current_order_customer'])

        messages.success(request, _('Order %s closed') % order.code)

        return redirect(order)

    data = {'order': order, 'action': request.path}
    return render(request, "orders/close.html", data)


@permission_required("servo.delete_order")
def reopen_order(request, pk):
    order = Order.objects.get(pk=pk)
    msg = order.reopen(request.user)
    messages.success(request, msg)
    return redirect(order)


@permission_required("servo.add_order")
def create(request, sn=None, device_id=None, product_id=None, note_id=None, customer_id=None):
    """
    Creates a new Service Order
    """
    order = Order(created_by=request.user)

    if customer_id is not None:
        order.customer_id = customer_id

    try:
        order.save()
    except Exception as e:
        messages.error(request, e)
        return redirect(list_orders)

    messages.success(request, _("Order %s created") % order.code)

    # create service order from a new device
    if sn is not None:
        order.add_device_sn(sn, request.user)

    if device_id is not None:
        device = Device.objects.get(pk=device_id)
        order.add_device(device, request.user)

    # creating an order from a product
    if product_id is not None:
        return redirect(add_product, order.pk, product_id)

    # creating an order from a note
    if note_id is not None:
        note = Note.objects.get(pk=note_id)
        note.order = order
        note.save()
        # try to match a customer
        if note.sender:
            try:
                customer = Customer.objects.get(email=note.sender)
                order.customer = customer
                order.save()
            except Customer.DoesNotExist:
                pass

    return redirect(order)


def list_orders(request):
    """
    orders/index
    """
    args = request.GET.copy()
    default = QueryDict('state={0}'.format(Order.STATE_QUEUED))

    if len(args) < 2: # search form not submitted
        args = request.session.get("order_search_filter", default)

    request.session['order_search_filter'] = args
    data = prepare_list_view(request, args)

    return render(request, "orders/index.html", data)


@permission_required("servo.change_order")
def toggle_tag(request, order_id, tag_id):
    tag = Tag.objects.get(pk=tag_id)
    order = Order.objects.get(pk=order_id)

    if tag not in order.tags.all():
        order.add_tag(tag)
    else:
        order.tags.remove(tag)

    return HttpResponse(tag.title)


@permission_required("servo.change_order")
def toggle_task(request, order_id, item_id):
    """
    Toggles a given Check List item in this order
    """
    checklist_item = ChecklistItem.objects.get(pk=item_id)
    
    try:
        item = ChecklistItemValue.objects.get(order_id=order_id, item=checklist_item)
        item.delete()
    except ChecklistItemValue.DoesNotExist:
        item = ChecklistItemValue()
        item.item = checklist_item
        item.order_id = order_id
        item.checked_by = request.user
        item.save()

    return HttpResponse(checklist_item.title)


def repair(request, order_id, repair_id):
    """
    Show the corresponding GSX Repair for this Service Order
    """
    repair = get_object_or_404(Repair, pk=repair_id)
    data = prepare_detail_view(request, order_id)
    data['repair'] = repair

    try:
        repair.connect_gsx(request.user)
        details = repair.get_details()
        try:
            data['notes'] = details.notes.encode('utf-8')
        except AttributeError:
            pass
        data['status'] = repair.update_status(request.user)
    except Exception as e:
        messages.error(request, e)

    data['parts'] = repair.servicepart_set.all()
    return render(request, "orders/repair.html", data)


@permission_required("servo.change_order")
def complete_repair(request, order_id, repair_id):
    repair = Repair.objects.get(pk=repair_id)
    if request.method == 'POST':
        try:
            repair.close(request.user)
            msg = _(u"Repair %s marked complete.") % repair.confirmation
            messages.success(request, msg)
        except GsxError, e:
            messages.error(request, e)

        return redirect(repair.order)

    return render(request, 'orders/close_repair.html', locals())


@csrf_exempt
@permission_required("servo.change_order")
def accessories(request, pk, device_id):
    from django.utils import safestring

    if request.POST.get('name'):
        a = Accessory(name=request.POST['name'])
        a.order_id = pk
        a.device_id = device_id
        a.save()

    choice_list = []
    choices = Accessory.objects.distinct('name')

    for c in choices:
        choice_list.append(c.name)

    action = reverse('orders-accessories', args=[pk, device_id])
    selected = Accessory.objects.filter(order_id=pk, device_id=device_id)
    choices_json = safestring.mark_safe(json.dumps(choice_list))

    return render(request, 'devices/accessories_edit.html', locals())


@permission_required('servo.change_order')
def delete_accessory(request, order_id, device_id, pk):
    Accessory.objects.filter(pk=pk).delete()
    return accessories(request, order_id, device_id)


@permission_required("servo.change_order")
def edit(request, pk):
    data = prepare_detail_view(request, pk)
    data['note_tags'] = Tag.objects.filter(type='note')
    return render(request, "orders/edit.html", data)


@permission_required('servo.delete_order')
def delete(request, pk):
    
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        return_to = order.get_queue_url()
        try:
            order.delete()
            del(request.session['current_order_id'])
            del(request.session['current_order_code'])
            del(request.session['current_order_customer'])
            messages.success(request, _(u'Order %s deleted') % order.code)
            return redirect(return_to)
        except Exception as e:
            ed = {'order': order.code, 'error': e}
            messages.error(request, _(u'Cannot delete order %(order)s: %(error)s') % ed)
            return redirect(order)

    action = request.path
    return render(request, "orders/delete_order.html", locals())


@permission_required('servo.change_order')
def toggle_follow(request, order_id):
    order = Order.objects.get(pk=order_id)
    data = {'icon': "open", 'action': _("Follow")}

    if request.user in order.followed_by.all():
        order.followed_by.remove(request.user)
    else:
        order.followed_by.add(request.user)
        data = {'icon': "close", 'action': _("Unfollow")}

    if request.is_ajax():
        return render(request, "orders/toggle_follow.html", data)

    return redirect(order)


def toggle_flagged(request, pk):
    order = Order.objects.get(pk=pk)
    t = FlaggedItem(content_object=order, flagged_by=request.user)
    t.save()


@permission_required("servo.change_order")
def remove_user(request, pk, user_id):
    """
    Removes this user from the follower list, unsets assignee
    """
    order = get_object_or_404(Order, pk=pk)
    user = User.objects.get(pk=user_id)

    try:
        order.remove_follower(user)
        if user == order.user:
            order.set_user(None, request.user)
        order.notify("unset_user", _('User %s removed from followers') % user, request.user)
    except Exception, e:
        messages.error(request, e)

    return redirect(order)


@permission_required("servo.change_order")
def update_order(request, pk, what, what_id):
    """
    Updates some things about an order
    """
    order = get_object_or_404(Order, pk=pk)
    what_id = int(what_id)

    if order.state is Order.STATE_CLOSED:
        messages.error(request, _("Closed orders cannot be modified"))
        return redirect(order)

    if what == "user":
        if request.method == "POST":
            fullname = request.POST.get("user")
            try:
                user = User.active.get(full_name=fullname)
                if order.user is None:
                    order.set_user(user, request.user)
                else:
                    order.add_follower(user)
                    order.save()
            except User.DoesNotExist:
                messages.error(request, _(u"User %s not found") % fullname)
        elif what_id > 0:
            user = User.objects.get(pk=what_id)
            order.set_user(user, request.user)

    if what == "queue":
        order.set_queue(what_id, request.user)

    if what == "status":
        order.set_status(what_id, request.user)

    if what == "priority":
        order.priority = what_id
        order.save()

    if what == "place" and request.method == "POST":
        place = request.POST.get("place")
        order.notify("set_place", place, request.user)
        order.place = place
        order.save()

    if what == "label" and request.method == "POST":
        label = request.POST.get("label")

        try:
            tag = Tag.objects.get(title=label, type="order")
            order.add_tag(tag, request.user)
        except Tag.DoesNotExist:
            messages.error(request, _(u"Label %s does not exist") % label)

    if what == "checkin":
        location = Location.objects.get(pk=what_id)
        order.checkin_location = location
        messages.success(request, _('Order updated'))
        order.save()

    if what == "checkout":
        location = Location.objects.get(pk=what_id)
        order.checkout_location = location
        messages.success(request, _('Order updated'))
        order.save()

    if what == "location":
        location = Location.objects.get(pk=what_id)
        msg = order.set_location(location, request.user)
        messages.success(request, msg)

    request.session['current_order_id'] = order.pk
    request.session['current_order_code'] = order.code
    if order.queue:
        request.session['current_order_queue'] = order.queue.pk

    return redirect(order)


def put_on_paper(request, pk, kind="confirmation"):
    """
    'Print' was taken?
    """
    conf = Configuration.conf()
    order = get_object_or_404(Order, pk=pk)

    title = _(u"Service Order #%s") % order.code
    notes = order.note_set.filter(is_reported=True)

    template = order.get_print_template(kind)
    
    if kind == "receipt":
        try:
            invoice = order.invoice_set.latest()
        except Exception as e:
            pass

    return render(request, template, locals())


@permission_required("servo.change_order")
def add_device(request, pk, device_id=None, sn=None):
    """
    Adds a device to a service order
    using device_id with existing devices or
    sn for new devices (which should have gone through GSX search)
    """
    order = get_object_or_404(Order, pk=pk)

    if device_id is not None:
        device = Device.objects.get(pk=device_id)

    if sn is not None:
        sn = sn.upper()
        # not using get() since SNs are not unique
        device = Device.objects.filter(sn=sn).first()

        if device is None:
            try:
                device = Device.from_gsx(sn)
                device.save()
            except Exception, e:
                messages.error(request, e)
                return redirect(order)

    try:
        event = order.add_device(device, request.user)
        messages.success(request, event)
    except Exception, e:
        messages.error(request, e)
        return redirect(order)

    if order.customer:
        order.customer.devices.add(device)

    return redirect(order)


@permission_required("servo.change_order")
def remove_device(request, order_id, device_id):
    action = request.path
    order = Order.objects.get(pk=order_id)
    device = Device.objects.get(pk=device_id)

    if request.method == "POST":
        msg = order.remove_device(device, request.user)
        messages.info(request, msg)
        return redirect(order)

    return render(request, "orders/remove_device.html", locals())


def events(request, order_id):
    data = prepare_detail_view(request, order_id)
    return render(request, "orders/events.html", data)


def device_from_product(request, pk, item_id):
    """
    Turns a SOI into a device and attaches it to this order
    """
    order = Order.objects.get(pk=pk)
    soi = ServiceOrderItem.objects.get(pk=item_id)

    try:
        GsxAccount.default(request.user, order.queue)
        device = Device.from_gsx(soi.sn)
        device.save()
        event = order.add_device(device, request.user)
        messages.success(request, event)
    except Exception, e:
        messages.error(request, e)

    return redirect(order)


@permission_required('servo.change_order')
def reserve_products(request, pk):
    order = Order.objects.get(pk=pk)
    location = request.user.get_location()

    if request.method == 'POST':

        for p in order.serviceorderitem_set.all():
            p.reserve_product()

        msg = _(u"Products of order %s reserved") % order.code
        order.notify("products_reserved", msg, request.user)
        messages.info(request, msg)

        return redirect(order)

    data = {'order': order, 'action': request.path}
    return render(request, "orders/reserve_products.html", data)


@permission_required("servo.change_order")
def edit_product(request, pk, item_id):
    """
    Edits a product added to an order
    """
    order = Order.objects.get(pk=pk)
    item = ServiceOrderItem.objects.get(pk=item_id)

    if not item.kbb_sn and item.product.part_type == "REPLACEMENT":
        try:
            device = order.devices.all()[0]
            item.kbb_sn = device.sn
        except IndexError:
            pass  # Probably no device in the order

    if item.product.component_code:
        try:
            GsxAccount.default(request.user, order.queue)
        except Exception, e:
            return render(request, "snippets/error_modal.html", {'error': e})

    form = OrderItemForm(instance=item)

    if request.method == "POST":
        form = OrderItemForm(request.POST, instance=item)
        if form.is_valid():
            try:
                item = form.save()
                # Set whoever set the KBB sn as the one who replaced the part
                if item.kbb_sn and not item.replaced_by:
                    item.replaced_by = request.user
                    item.save()

                messages.success(request, _(u"Product %s saved") % item.code)

                return redirect(order)
            except Exception, e:
                messages.error(request, e)

    product = item.product
    title = product.code
    prices = json.dumps(item.product.get_price())

    return render(request, "orders/edit_product.html", locals())


@permission_required("servo.change_order")
def add_product(request, pk, product_id):
    "Adds this product to this Sales Order"
    order = Order.objects.get(pk=pk)
    product = Product.objects.get(pk=product_id)
    order.add_product(product, 1, request.user)
    messages.success(request, _(u'Product %s added') % product.code)

    return redirect(order)


@permission_required("servo.change_order")
def add_part(request, pk, device, code):
    """
    Adds a part for this device to this order
    """
    gsx_product = cache.get(code)
    order = Order.objects.get(pk=pk)
    device = Device.objects.get(pk=device)

    try:
        product = Product.objects.get(code=code)
        if not product.fixed_price:
            product.update_price(gsx_product)
    except Product.DoesNotExist:
        product = gsx_product

    product.save()

    try:
        tag, created = TaggedItem.objects.get_or_create(
            content_type__model="product",
            object_id=product.pk,
            tag=device.description
        )
        tag.save()
    except DatabaseError:
        pass

    order.add_product(product, 1, request.user)

    return render(request, "orders/list_products.html", locals())


def choose_product(request, order_id):
    pass


@permission_required("servo.change_order")
def report_product(request, pk, item_id):
    product = ServiceOrderItem.objects.get(pk=item_id)
    product.should_report = not product.should_report
    product.save()

    if product.should_report:
        return HttpResponse('<i class="icon-ok"></i>')

    return HttpResponse('<i class="icon-ok icon-white"></i>')


@permission_required("servo.change_order")
def report_device(request, pk, device_id):
    device = OrderDevice.objects.get(pk=device_id)
    device.should_report = not device.should_report
    device.save()

    if device.should_report:
        return HttpResponse('<i class="icon-ok"></i>')

    return HttpResponse('<i class="icon-ok icon-white"></i>')


@permission_required('servo.change_order')
def remove_product(request, pk, item_id):
    order = Order.objects.get(pk=pk)

    # The following is to help those who hit Back after removing a product
    try:
        item = ServiceOrderItem.objects.get(pk=item_id)
    except ServiceOrderItem.DoesNotExist:
        messages.error(request, _("Order item does not exist"))
        return redirect(order)

    if request.method == 'POST':
        msg = order.remove_product(item, request.user)
        messages.info(request, msg)
        return redirect(order)

    return render(request, 'orders/remove_product.html', locals())


@permission_required('servo.change_order')
def products(request, pk, item_id=None, action='list'):
    order = Order.objects.get(pk=pk)
    if action == 'list':
        return render(request, 'orders/products.html', {'order': order})


@permission_required('servo.change_order')
def list_products(request, pk):
    order = Order.objects.get(pk=pk)
    return render(request, "orders/list_products.html", locals())


def parts(request, order_id, device_id, queue_id):
    """
    Selects parts for this device in this order
    """
    order = Order.objects.get(pk=order_id)
    device = Device.objects.get(pk=device_id)
    title = device.description
    url = reverse('devices-parts', args=[device_id, order_id, queue_id])

    if order.queue is not None:
        request.session['current_queue'] = order.queue.pk

    return render(request, "orders/parts.html", locals())


@permission_required("servo.change_order")
def select_customer(request, pk, customer_id):
    """
    Selects a specific customer for this order
    """
    order = Order.objects.get(pk=pk)
    order.customer_id = customer_id
    order.save()

    return redirect(order)


@permission_required("servo.change_order")
def choose_customer(request, pk):
    """
    Lets the user search for a customer for this order
    """
    if request.method == "POST":
        customers = Customer.objects.none()
        kind = request.POST.get('kind')
        query = request.POST.get('name')

        if len(query) > 2:
            customers = Customer.objects.filter(
                Q(fullname__icontains=query)
                | Q(email__icontains=query)
                | Q(phone__contains=query)
            )

        if kind == 'companies':
            customers = customers.filter(is_company=True)

        if kind == 'contacts':
            customers = customers.filter(is_company=False)

        data = {'customers': customers, 'order_id': pk}
        return render(request, "customers/choose-list.html", data)

    data = {'action': request.path}
    return render(request, 'customers/choose.html', data)


@permission_required("servo.change_order")
def remove_customer(request, pk, customer_id):
    if request.method == "POST":
        order = Order.objects.get(pk=pk)
        customer = Customer.objects.get(pk=customer_id)
        order.customer = None
        order.save()
        msg = _(u"Customer %s removed") % customer.name
        order.notify("customer_removed", msg, request.user)
        messages.success(request, msg)
        return redirect(order)

    data = {'action': request.path}
    return render(request, "orders/remove_customer.html", data)


def search(request):
    query = request.GET.get("q")

    if not query or len(query) < 3:
        messages.error(request, _('Search query is too short'))
        return redirect(list_orders)

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

    data = {'title': _(u'Search results for "%s"') % query}
    data['orders'] = orders.distinct()

    return render(request, "orders/index.html", data)


@permission_required("servo.add_order")
def copy_order(request, pk):
    order = Order.objects.get(pk=pk)
    new_order = order.duplicate(request.user)
    return redirect(new_order)


def history(request, pk, device):
    device = get_object_or_404(Device, pk=device)
    orders = device.order_set.exclude(pk=pk)
    return render(request, "orders/history.html", locals())


@permission_required("servo.batch_process")
def batch_process(request):
    form = BatchProcessForm()
    title = _('Batch Processing')

    if request.method == 'POST':
        form = BatchProcessForm(request.POST)
        if form.is_valid():
            from servo.tasks import batch_process
            batch_process.delay(request.user, form.cleaned_data)
            messages.success(request, _('Request accepted for batch processing'))

    return render(request, "orders/batch_process.html", locals())


def download_results(request):
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    header = [
        'CODE',
        'CUSTOMER',
        'CREATED_AT',
        'ASSIGNED_TO',
        'CHECKED_IN',
        'LOCATION'
    ]
    writer.writerow(header)

    for o in request.session['order_queryset']:
        row = [o.code, o.customer, o.created_at, 
            o.user, o.checkin_location, o.location]
        coded = [unicode(s).encode('utf-8') for s in row]

        writer.writerow(coded)

    return response
