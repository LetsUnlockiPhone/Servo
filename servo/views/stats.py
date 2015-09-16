# -*- coding: utf-8 -*-

import json
import datetime
from datetime import timedelta
from django.utils import timezone

from django import forms
from django.db import connection
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page

from servo.stats.forms import *
from servo.stats.queries import *

from servo.models import User, Order


class ServoTimeDelta:
    def __init__(self, td):
        self.td = td

    def days(self):
        return self.td.days

    def workdays(self):
        pass

    def hours(self):
        return self.td.seconds//3600

    def nonzero(self):
        return self.hours() > 0


def prep_view(request):
    """
    Prepares the stats view
    """
    title = _('Statistics')
    profile = request.user
    location = request.user.location

    initial = {
        'location'  : location.pk,
        'end_date'  : str(default_end_date),
        'start_date': str(default_start_date),
        'timescale' : default_timescale,
    }

    group = request.user.get_group()

    if group:
        initial['group'] = group.pk

    # Remember the previous stats filter
    if request.session.get('stats_filter'):
        initial.update(request.session['stats_filter'])

    request.session['stats_filter'] = initial

    return locals()


def index(request):
    """
    /stats/
    """
    data = prep_view(request)
    form = TechieStatsForm(initial=data['initial'])

    if request.method == 'POST':
        form = TechieStatsForm(request.POST, initial=data['initial'])
        if form.is_valid():
            request.session['stats_filter'] = form.serialize()

    data['form'] = form
    return render(request, "stats/index.html", data)


#@cache_page(15*60)
def data(request, query):
    result  = []
    stats   = StatsManager()
    cursor  = connection.cursor()
    report, what = query.split('/')

    locations   = request.user.locations
    params      = request.session.get('stats_filter')
    timescale   = params.get('timescale', default_timescale)
    location    = params.get('location', request.user.location)

    if params.get('location'):
        location = Location.objects.get(pk=params['location'])
    else:
        location = request.user.location

    try:
        location_id = location.pk
    except AttributeError:
        location_id = 0

    start_date  = params.get('start_date', default_start_date)
    end_date    = params.get('end_date', default_end_date)
    queues      = request.user.queues.all()

    try:
        users = params.get('group').user_set
    except AttributeError:
        users = User.objects.filter(location=location)

    if report == "sales":
        if what == "invoices":
            for i in queues:
                data = stats.sales_invoices(timescale, i.pk, start_date, end_date)
                result.append({'label': i.title, 'data': data})

        if what == "purchases":
            for i in queues:
                data = stats.sales_purchases(timescale, i.pk, start_date, end_date)
                result.append({'label': i.title, 'data': data})

        if what == "parts":
            i = 0
            data = []
            labels = []
            results = stats.sales_parts_per_labtier(start_date, end_date)
            for r in results:
                data.append([i, r[1]])
                labels.append([i, r[0]])
                i += 1

            result.append({'label': labels, 'data': data})

    if what == "personal":
        location_id = request.user.get_location().id
        users = User.objects.filter(pk=request.user.pk)

        for i in users.filter(is_active=True):
            data = stats.order_runrate(timescale, location_id, i.pk, start_date, end_date)
            result.append({'label': i.get_full_name(), 'data': data})

    if what == "runrate":
        for i in users.filter(is_active=True):
            data = stats.order_runrate(timescale, location_id, i.pk, start_date, end_date)
            result.append({'label': i.get_full_name(), 'data': data})

    if report == "created":
        if what == "user":
            for i in location.user_set.all():
                data = stats.orders_created_by(timescale,
                                               location_id,
                                               i.pk,
                                               start_date,
                                               end_date)
                result.append({'label': i.get_full_name(), 'data': data})

        if what == "location":
            for i in locations.all():
                data = stats.orders_created_at(timescale, i.pk, start_date, end_date)
                result.append({'label': i.title, 'data': data})

    if report == "closed":
        if what == "location":
            for i in locations.all():
                data = stats.orders_closed_at(timescale, i.pk, start_date, end_date)
                result.append({'label': i.title, 'data': data})
        if what == "queue":
            for i in queues:
                data = stats.orders_closed_in(
                    timescale,
                    location.pk,
                    i.pk,
                    start_date,
                    end_date)
                result.append({'label': i.title, 'data': data})

    if what == "count":
        for i in queues:
            data = stats.order_count(timescale, location_id, i.pk, start_date, end_date)
            result.append({'label': i.title, 'data': data})

    if report == "status":
        status = params.get('status')
        if what == "location":
            for i in locations.all():
                data = stats.statuses_per_location(
                    timescale, 
                    i.pk,
                    status,
                    start_date,
                    end_date)
                result.append({'label': i.title, 'data': data})
        if what == "tech":
            for i in User.objects.filter(location=location, is_active=True):
                data = stats.statuses_per_user(
                    timescale,
                    i.pk,
                    status,
                    start_date,
                    end_date)
                result.append({'label': i.get_name(), 'data': data})

    if report == "turnaround":
        if what == "location":
            for i in locations.all():
                data = stats.turnaround_per_location(
                    timescale,
                    i.pk,
                    start_date,
                    end_date)
                result.append({'label': i.title, 'data': data})

    if report == "runrate":
        if what == "location":
            for i in locations.all():
                data = stats.runrate_per_location(
                    timescale,
                    i.pk,
                    start_date,
                    end_date)
                result.append({'label': i.title, 'data': data})

    if report == "distribution":
        if what == "location":
            result = stats.distribution_per_location(start_date, end_date)

    if what == "turnaround":
        for i in queues:
            data = stats.order_turnaround(
                timescale,
                location_id,
                i.pk,
                start_date,
                end_date
            )
            result.append({'label': i.title, 'data': data})

    if what == "queues":
        cursor.execute("""SELECT q.title, COUNT(*)
            FROM servo_order o LEFT OUTER JOIN servo_queue q on (o.queue_id = q.id)
            WHERE (o.created_at, o.created_at) OVERLAPS (%s, %s)
            GROUP BY q.title""", [start_date, end_date])

        for k, v in cursor.fetchall():
            k = k or _('No Queue')
            result.append({'label': k, 'data': v})

    if what == "techs":
        for i in users.filter(is_active=True):
            cursor.execute("""SELECT COUNT(*) as p
                FROM servo_order o
                WHERE user_id = %s
                    AND location_id = %s
                    AND (created_at, created_at) OVERLAPS (%s, %s)
                GROUP BY user_id""", [i.pk, location_id, start_date, end_date])

            for v in cursor.fetchall():
                result.append({'label': i.username, 'data': v})

    return HttpResponse(json.dumps(result))


def sales(request):
    data = prep_view(request)
    form = InvoiceStatsForm(initial=data['initial'])

    if request.method == 'POST':
        form = InvoiceStatsForm(request.POST, initial=data['initial'])
        if form.is_valid():
            request.session['stats_filter'] = form.serialize()

    data['form'] = form
    return render(request, "stats/sales.html", data)


def queues(request):
    data = prep_view(request)
    form = OrderStatsForm(initial=data['initial'])
    if request.method == 'POST':
        form = OrderStatsForm(request.POST, initial=data['initial'])
        if form.is_valid():
            request.session['stats_filter'] = form.serialize()

    data['form'] = form
    return render(request, "stats/queues.html", data)


def locations(request):
    data = prep_view(request)
    form = BasicStatsForm(initial=data['initial'])
    if request.method == 'POST':
        form = BasicStatsForm(request.POST, initial=data['initial'])
        if form.is_valid():
            request.session['stats_filter'] = form.serialize()
    data['form'] = form
    return render(request, "stats/locations.html", data)


def statuses(request):
    data = prep_view(request)
    form = StatusStatsForm(initial=data['initial'])
    if request.method == 'POST':
        form = StatusStatsForm(request.POST, initial=data['initial'])
        if form.is_valid():
            # Store the name of the status since we don't have
            # IDs in events, yet
            status = form.cleaned_data['status'].title
            f = form.serialize()
            f['status'] = status
            request.session['stats_filter'] = f

    data['form'] = form
    return render(request, "stats/statuses.html", data)


def repairs(request):
    title = _('Repair statistics')
    form = NewStatsForm(initial={
        'location': [request.user.location],
        'queue': request.user.queues.all()
    })

    if request.GET.get('location'):
        results = []
        form = NewStatsForm(request.GET)
        totals = {
            'created'      : 0,
            'assigned'     : 0,
            'repairs'      : 0,
            'dispatched'   : 0,
            'tmp_orders'   : [],
            'turnaround'   : timedelta(),
        }

        if not form.is_valid():
            return render(request, "stats/newstats.html", locals())

        cdata = form.cleaned_data
        date_range = (cdata['start_date'], cdata['end_date'])

        for u in User.active.filter(location=cdata['location']):
            r = {'name': u.get_full_name()}

            # Look at invoices first because that data may be different from
            # assignment info (tech A startx, tech B finishes)
            dispatched = u.invoice_set.filter(
                order__queue=cdata['queue'],
                order__location=cdata['location'],
                created_at__range=date_range
            )

            if len(cdata.get('label')):
                dispatched = dispatched.filter(order__tags=cdata['label'])

            # Count each case's dispatch only once
            r['dispatched'] = dispatched.values('order_id').distinct().count()

            created = u.created_orders.filter(
                queue=cdata['queue'],
                location=cdata['location'],
                created_at__range=date_range
            )

            if len(cdata.get('label')):
                created = created.filter(tags=cdata['label'])

            r['created'] = created.count()
            totals['created'] += r['created'] # add amount to totals

            assigned = u.order_set.filter(
                queue=cdata['queue'],
                location=cdata['location'],
                started_at__range=date_range
            )

            if len(cdata.get('label')):
                assigned = assigned.filter(tags=cdata['label'])

            r['assigned'] = assigned.count()

            if (r['assigned'] < 1) and (r['dispatched'] < 1):
                continue # ... only continue with actual techs

            repairs = u.created_repairs.filter(
                order__queue=cdata['queue'],
                order__location=cdata['location'],
                submitted_at__range=date_range
            )

            if len(cdata.get('label')):
                repairs = repairs.filter(order__tags=cdata['label'])

            # Only count each case's GSX repair once
            r['repairs'] = repairs.values('order_id').distinct().count()

            totals['repairs']    += r['repairs']
            totals['assigned']   += r['assigned']
            totals['dispatched'] += r['dispatched']

            results.append(r)
            turnaround = timedelta()

            # calculate turnaround time of dispatched cases
            for o in dispatched:
                totals['tmp_orders'].append(o.order)
                for s in o.order.orderstatus_set.filter(status=cdata['status']):
                    if s.finished_at is None:
                        s.finished_at = s.order.closed_at or timezone.now()

                    totals['turnaround'] += (s.finished_at - s.started_at)

        totals['diff'] = totals['dispatched'] - totals['assigned']

        if totals['dispatched'] > 0:
            totals['turnaround'] = ServoTimeDelta(totals['turnaround']/totals['dispatched'])

    return render(request, "stats/newstats.html", locals())
