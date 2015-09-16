# -*- coding: utf-8 -*-

import json
from django.utils import timezone
from django.http import HttpResponse
from django.core.exceptions import FieldError
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView

from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import (api_view, authentication_classes, permission_classes)

from servo.api.serializers import *

from servo.models import *


def dumps(obj):
    import datetime
    data = {}
    for f in obj.api_fields:
        value = getattr(obj, f)
        if type(value) in (datetime.datetime, datetime.date,):
            value = value.isoformat()
        data[f] = value
    return json.dumps(data)


class OrderStatusView(DetailView):

    model = Order

    def get(self, *args):
        args = self.request.GET
        if not args.get('q'):
            error = {'error': 'Need parameter for query'}
            return HttpResponse(json.dumps(error),
                                status=400,
                                content_type='application/json')

        self.code = args.get('q')
        self.object = get_object_or_404(Order, code=self.code)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        out = {
            'order': self.object.code,
            'status': self.object.get_status_name(),
            'status_description': self.object.get_status_description(),
        }

        if Configuration.conf('checkin_timeline'):
            timeline = []
            for i in self.object.orderstatus_set.exclude(status=None):
                status = {'badge': i.get_badge()}
                status['status'] = i.status.title
                status['started_at'] = i.started_at.isoformat()
                status['description'] = i.status.description
                timeline.append(status)

            out['timeline'] = timeline

        return HttpResponse(json.dumps(out), content_type='application/json')


def tags(request):
    results = Tag.objects.filter(**request.GET.dict())
    data = results.distinct().values_list("title", flat=True)
    return HttpResponse(json.dumps(list(data)), content_type='application/json')


def statuses(request):
    from servo.models import Status
    results = Status.objects.all()
    data = serialize('json', results)
    return HttpResponse(data, content_type='application/json')


def locations(request):
    queryset = Location.objects.all()
    serializer = 'json'
    if request.META['HTTP_USER_AGENT'].startswith('curl'):
        serializer = 'yaml'
    data = serialize(serializer, queryset)
    return HttpResponse(data)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def users(request):
    query = request.GET.dict()
    queryset = User.active.filter(**query)
    data = list(queryset.values_list("full_name", flat=True))
    return HttpResponse(json.dumps(data), content_type='application/json')


def places(request):
    places = Order.objects.exclude(place=None)
    places = places.order_by("place").distinct("place").values_list('place', flat=True)
    return HttpResponse(json.dumps(list(places)), content_type='application/json')


def queues(request):
    queryset = Queue.objects.all()
    data = serialize('json', queryset, fields=('pk', 'title'))
    return HttpResponse(data, content_type='application/json')


def json_response(data):
    return HttpResponse(json.dumps(data), content_type='application/json')


def ok(message):
    msg = json.dumps(dict(ok=message))
    return HttpResponse(msg, content_type='application/json')


def error(message):
    msg = json.dumps(dict(error=str(message)))
    return HttpResponse(msg, content_type='application/json')


def client_error(message):
    msg = json.dumps(dict(error=str(message)))
    return HttpResponse(msg, content_type='application/json', status=400)


def create_order(request):
    try:
        data = json.loads(request.body)
    except ValueError as e:
        return client_error('Malformed request: %s' % e)

    cdata = data.get('customer')
    problem = data.get('problem')

    if not cdata:
        return client_error('Cannot create order without customer info')

    if not problem:
        return client_error('Cannot create order without problem description')

    try:
        customer, created = Customer.objects.get_or_create(
            name=cdata['name'],
            email=cdata['email']
            )
    except Exception as e:
        return client_error('Invalid customer details: %s' % e)

    if request.user.customer:
        customer.parent = request.user.customer

    if cdata.get('city'):
        customer.city = cdata.get('city')

    if cdata.get('phone'):
        customer.phone = cdata.get('phone')

    if cdata.get('zip_code'):
        customer.zip_code = cdata.get('zip_code')

    if cdata.get('street_address'):
        customer.street_address = cdata.get('street_address')

    customer.save()

    order = Order(created_by=request.user, customer=customer)
    order.save()

    note = Note(created_by=request.user, body=problem, is_reported=True)
    note.order = order
    note.save()

    if data.get('attachment'):
        import base64
        from servo.models import Attachment
        from django.core.files.base import ContentFile

        attachment = data.get('attachment')

        try:
            filename = attachment.get('name')
            content = base64.b64decode(attachment.get('data'))
        except Exception as e:
            return client_error('Invalid file data: %s' %e)

        content = ContentFile(content, filename)
        attachment = Attachment(content=content, content_object=note)
        attachment.save()
        attachment.content.save(filename, content)
        note.attachments.add(attachment)

    if data.get('device'):

        try:
            GsxAccount.default(request.user)
        except Exception as e:
            pass

        ddata = data.get('device')

        try:
            device = order.add_device_sn(ddata.get('sn'), request.user)
        except Exception as e:
            device = Device(sn=ddata.get('sn', ''))
            device.description = ddata.get('description', '')
            device.save()
            order.add_device(device)

        for a in ddata.get('accessories', []):
            a = Accessory(name=a, order=order, device=device)
            a.save()

    return ok(order.code)


@api_view(['GET', 'POST', 'PUT'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def orders(request, code=None, pk=None):
    """
    This is the orders API
    """
    from servo.api.serializers import OrderSerializer

    if request.method == 'POST':
        return create_order(request)

    if request.method == 'PUT':
        return error('Method not yet implemented')

    if request.GET.get('q'):
        results = Order.objects.filter(**request.GET)

    if pk:
        order = Order.objects.get(pk=pk)
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)

    if code:
        order = Order.objects.get(code=code)
        if order.status:
            order.status_description = order.status.status.description
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)

    orders = Order.objects.none()
    serializer = OrderSerializer(orders, many=True, context={'request': request})
    return Response(serializer.data)


def messages(request):
    """
    Responds to SMS status updates
    """
    from servo.messaging.sms import SMSJazzProvider, HQSMSProvider

    if not request.GET.get('id'):
        return HttpResponse('Thanks, but no thanks')

    m = get_object_or_404(Message, code=request.GET['id'])
    gw = Configuration.conf('sms_gateway')
    statusmap = HQSMSProvider.STATUSES

    if gw == 'jazz':
        statusmap = SMSJazzProvider.STATUSES

    status = statusmap[request.GET['status']]
    m.status = status[0]
    m.error = status[1]

    if m.status == 'DELIVERED':
        m.received_at = timezone.now()

    if m.status == 'FAILED':
        if m.note.order:
            uid = Configuration.conf('imap_act')
            if uid:
                user = User.objects.get(pk=uid)
                m.note.order.notify('sms_failed', m.error, user)

    m.save()

    return HttpResponse('OK')


def device_models(request):
    data = Device.objects.order_by("description").distinct("description")
    return json_response(list(data.values_list("description", flat=True)))


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def warranty(request):
    from servo.api.serializers import DeviceSerializer
    sn = request.GET.get('sn')

    if not sn:
        return error('Need query parameter for warranty lookup')

    try:
        GsxAccount.default(request.user)
    except Exception as e:
        return error('Cannot connect to GSX (check user name and password)')

    try:
        result = Device.from_gsx(sn, cached=False)
        serializer = DeviceSerializer(result, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return error(e)


@api_view(['GET'])
def order_status(request):
    from servo.api.serializers import OrderStatusSerializer
    code = request.GET.get('q')
    try:
        result = Order.objects.get(code=code)
        #serializer = OrderStatusSerializer(result)
        return Response(serializer.data)
    except Exception as e:
        return (error(e))


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def notes(request, pk=None):
    if pk:
        note = Note.objects.get(pk=pk)
        serializer = NoteSerializer(note, context={'request': request})
        return Response(serializer.data)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def order_items(request, pk):
    item = ServiceOrderItem.objects.get(pk=pk)
    serializer = ServiceOrderItemSerializer(item, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def user_detail(request, pk):
    user = User.objects.get(pk=pk)
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def customers(request, pk=None):
    customer = Customer.objects.get(pk=pk)
    serializer = CustomerSerializer(customer, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def devices(request, pk=None):
    device = Device.objects.get(pk=pk)
    serializer = DeviceSerializer(device, context={'request': request})
    return Response(serializer.data)
