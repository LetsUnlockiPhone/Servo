# -*- coding: utf-8 -*-

import json
import locale

from gsxws import products, GsxError

from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.core.cache import cache

from django.utils import translation
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied

from servo.lib.utils import json_response
from servo.views.order import put_on_paper
from servo.validators import apple_sn_validator
from servo.models import (User, Device, GsxAccount, Order,
                          Customer, Location, Note, Attachment,
                          Configuration, ChecklistItem, Tag,)
from servo.forms import (SerialNumberForm, AppleSerialNumberForm,
                         DeviceForm, IssueForm, CustomerForm,
                         QuestionForm, AttachmentForm, StatusCheckForm,)


def find_device(request):
    device = Device(sn=request.GET['sn'])
    device.description = _('Other Device')
    device_form = DeviceForm(instance=device)

    try:
        apple_sn_validator(device.sn)
    except Exception as e: # not an Apple serial number
        return render(request, "checkin/device_form.html", locals())

    try:
        device = get_device(request, device.sn)
        device_form = DeviceForm(instance=device)
    except GsxError as e:
        error = e

    return render(request, "checkin/device_form.html", locals())


def find_customer(request, phone):
    if not request.user.is_authenticated():
        raise PermissionDenied

    results = []

    for c in Customer.objects.filter(phone=phone):
        title = '%s - %s' % (c.phone, c.name)
        results.append({'id': c.pk, 'name': c.name, 'title': title})

    return json_response(results)


def init_locale(request):
    lc = settings.INSTALL_LOCALE.split('.')
    locale.setlocale(locale.LC_TIME, lc)
    locale.setlocale(locale.LC_NUMERIC, lc)
    locale.setlocale(locale.LC_MESSAGES, lc)
    locale.setlocale(locale.LC_MONETARY, lc)

    translation.activate(settings.INSTALL_LANGUAGE)
    request.session[translation.LANGUAGE_SESSION_KEY] = settings.INSTALL_LANGUAGE


def set_cache_device(device):
    key = 'checkin-device-%s' % device.sn
    cache.set(key, device)


def get_gsx_connection(request):
    act = GsxAccount.get_default_account()
    user = User.objects.get(pk=request.session['checkin_user'])
    location = Location.objects.get(pk=request.session['checkin_location'])
    return act.connect(user, location)


def get_remote_device(request, sn):
    try:
        apple_sn_validator(sn)
    except ValidationError:
        return Device(sn=sn, image_url='https://static.servoapp.com/images/na.gif')

    get_gsx_connection(request)

    return Device.from_gsx(sn)


def get_local_device(request, sn):
    try:
        device = Device.objects.filter(sn=sn)[0]
    except IndexError:
        device = get_remote_device(request, sn)

    return device


def get_device(request, sn):
    if len(sn) < 1:
        return Device(sn=sn)

    key = 'checkin-device-%s' % sn
    device = cache.get(key, get_local_device(request, sn))
    set_cache_device(device)
    return device


def init_session(request):
    # initialize some basic vars
    if not request.user.is_authenticated():
        request.session.flush()

    # initialize locale
    init_locale(request)

    request.session['checkin_device']   = None
    request.session['checkin_customer'] = None

    user = User.get_checkin_user()
    location = user.location

    if not request.session.get('company_name'):
        request.session['company_name'] = Configuration.conf('company_name')

    if request.user.is_authenticated():

        # these are our fallback defaults
        user = request.user
        location = user.location

        try:
            location_id = request.GET['l']
        except KeyError:
            # not given - try session, then default to user's location
            location_id = request.session.get('checkin_location', location.pk)
        finally:
            location = get_object_or_404(Location, pk=location_id)

        try:
            user_id = request.GET['u']
        except KeyError:
            # not given - default to session, then auth user
            user_id = request.session.get('checkin_user', user.pk)
        
        user = get_object_or_404(User, pk=user_id)
        request.session['checkin_locations'] = Location.get_checkin_list()

        checkin_users = User.get_checkin_group()
        queryset = checkin_users.filter(location=location)
        request.session['checkin_users'] = User.serialize(queryset)
    
    request.session['checkin_user'] = user.pk
    request.session['checkin_location'] = location.pk
    request.session['checkin_user_name'] = user.get_name()
    request.session['checkin_location_name'] = location.title


def reset(request):
    init_session(request)
    return redirect(index)


def thanks(request, order):
    """
    Final step/confirmation
    """
    title = _('Done!')

    try:
        request.session.delete_test_cookie()
    except KeyError:
        pass # ignore spurious KeyError at /checkin/thanks/RJTPS/

    try:
        order = Order.objects.get(url_code=order)
    except Order.DoesNotExist:
        messages.error(request, _('Order does not exist'))
        return redirect(reset)

    return render(request, "checkin/thanks.html", locals())


def get_customer(request):
    """
    Returns the selected customer data
    """
    if not request.user.is_authenticated():
        raise PermissionDenied

    if not request.GET.get('c'):
        return

    customer = get_object_or_404(Customer, pk=request.GET['c'])
    request.session['checkin_customer'] = customer.pk

    fdata = {'fname': customer.firstname, 'lname': customer.lastname}
    fdata['city'] = customer.city
    fdata['email'] = customer.email
    fdata['phone'] = customer.phone
    fdata['country'] = customer.country
    fdata['postal_code'] = customer.zip_code
    fdata['address'] = customer.street_address

    return json_response(fdata)


def status(request):
    """
    Status checking through the checkin
    """
    title = _('Repair Status')

    if request.GET.get('code'):
        timeline = []
        form = StatusCheckForm(request.GET)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                order = Order.objects.get(code=code)
                status_description = order.get_status_description()
                if Configuration.conf('checkin_timeline'):
                    timeline = order.orderstatus_set.all()
                if order.status is None:
                    order.status_name = _(u'Waiting to be processed')
            except Order.DoesNotExist:
                messages.error(request, _(u'Order %s not found') % code)
            return render(request, "checkin/status-show.html", locals())
    else:
        form = StatusCheckForm()

    return render(request, "checkin/status.html", locals())


def print_confirmation(request, code):
    order = get_object_or_404(Order, url_code=code)
    return put_on_paper(request, order.pk)


def terms(request):
    conf = Configuration.conf()
    return render(request, 'checkin/terms.html', locals())


@never_cache
def index(request):
    """
    The checkin page
    @FIXME: would be nice to break this into smaller chunks...
    """

    request.session.set_test_cookie()
    if not request.session.test_cookie_worked():
        return

    if request.method == 'GET':
        init_session(request)
        
    title = _('Service Order Check-In')

    dcat = request.GET.get('d', 'mac')
    dmap = {
        'mac'       : _('Mac'),
        'iphone'    : _('iPhone'),
        'ipad'      : _('iPad'),
        'ipod'      : _('iPod'),
        'acc'       : _('Apple Accessory'),
        'beats'     : _('Beats Products'),
        'other'     : _('Other Devices'),
    }

    issue_form = IssueForm()
    device = Device(description=dmap[dcat])

    if dcat in ('mac', 'iphone', 'ipad', 'ipod'):
        sn_form = AppleSerialNumberForm()
    else:
        sn_form = SerialNumberForm()

    tags = Tag.objects.filter(type="order")
    device_form = DeviceForm(instance=device)
    customer_form =  CustomerForm(request)

    if request.method == 'POST':

        sn_form = SerialNumberForm(request.POST)
        issue_form = IssueForm(request.POST, request.FILES)
        customer_form = CustomerForm(request, request.POST)
        device_form = DeviceForm(request.POST, request.FILES)

        if device_form.is_valid() and issue_form.is_valid() and customer_form.is_valid():

            user = get_object_or_404(User, pk=request.session['checkin_user'])

            idata = issue_form.cleaned_data
            ddata = device_form.cleaned_data
            cdata = customer_form.cleaned_data
            customer_id = request.session.get('checkin_customer')

            if customer_id:
                customer = get_object_or_404(Customer, pk=customer_id)
            else:
                customer = Customer()

            name = u'{0} {1}'.format(cdata['fname'], cdata['lname'])
            
            if len(cdata['company']):
                name += ', ' + cdata['company']

            customer.name  = name
            customer.city  = cdata['city']
            customer.phone = cdata['phone']
            customer.email = cdata['email']
            customer.phone = cdata['phone']
            customer.zip_code = cdata['postal_code']
            customer.street_address = cdata['address']
            customer.save()

            order = Order(customer=customer, created_by=user)
            order.location_id = request.session['checkin_location']
            order.checkin_location = cdata['checkin_location']
            order.checkout_location = cdata['checkout_location']

            order.save()
            order.check_in(user)

            try:
                device = get_device(request, ddata['sn'])
            except GsxError as e:
                pass

            device.username = ddata['username']
            device.password = ddata['password']
            device.description = ddata['description']
            device.purchased_on = ddata['purchased_on']
            device.purchase_country = ddata['purchase_country']
            device.save()
            
            order.add_device(device, user)

            note = Note(created_by=user, body=idata['issue_description'])
            note.is_reported = True
            note.order = order
            note.save()

            # Proof of purchase was supplied
            if ddata.get('pop'):
                f = {'content_type': Attachment.get_content_type('note').pk}
                f['object_id'] = note.pk
                a = AttachmentForm(f, {'content': ddata['pop']})
                a.save()

            if request.POST.get('tags'):
                order.set_tags(request.POST.getlist('tags'), request.user)

            # Check checklists early for validation
            answers = []

            # @FIXME: should try to move this to a formset...
            for k, v in request.POST.items():
                if k.startswith('__cl__'):
                    answers.append('- **' + k[6:] + '**: ' + v)

            if len(answers) > 0:
                note = Note(created_by=user, body="\r\n".join(answers))

                if Configuration.true('checkin_report_checklist'):
                    note.is_reported = True

                note.order = order
                note.save()

            # mark down internal notes (only if logged in)
            if len(idata.get('notes')):
                note = Note(created_by=user, body=idata['notes'])
                note.is_reported = False
                note.order = order
                note.save()

            # mark down condition of device
            if len(ddata.get('condition')):
                note = Note(created_by=user, body=ddata['condition'])
                note.is_reported = True
                note.order = order
                note.save()

            # mark down supplied accessories
            if len(ddata.get('accessories')):
                accs = ddata['accessories'].strip().split("\n")
                order.set_accessories(accs, device)

            redirect_to = thanks

            """
            if request.user.is_authenticated():
                if request.user.autoprint:
                    redirect_to = print_confirmation
            """
            return redirect(redirect_to, order.url_code)

    try:
        pk = Configuration.conf('checkin_checklist')
        questions = ChecklistItem.objects.filter(checklist_id=pk)
    except ValueError:
        # Checklists probably not configured
        pass

    if request.GET.get('phone'):
        return find_customer(request, request.GET['phone'])

    if request.GET.get('sn'):
        return find_device(request)

    return render(request, "checkin/newindex.html", locals())
