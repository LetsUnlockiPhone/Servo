# -*- coding: utf-8 -*-

import csv
import pytz
from datetime import date

from django.contrib import auth
from django.utils import timezone, translation

from django.contrib import messages
from django.http import QueryDict
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from dateutil.relativedelta import relativedelta
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render, get_object_or_404

from servo.lib.utils import paginate
from servo.views.order import prepare_list_view

from servo.models import Order, User, Calendar, CalendarEvent
from servo.forms.account import ProfileForm, RegistrationForm, LoginForm


def settings(request):
    """
    User editing their profile preferences
    """
    title = _("Profile Settings")
    form = ProfileForm(instance=request.user)

    if request.method == "POST":

        form = ProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            user = form.save()
            messages.success(request, _("Settings saved"))
            User.refresh_nomail()
            
            if form.cleaned_data['password1']:
                request.user.set_password(form.cleaned_data['password1'])
                request.user.save()

            lang = user.activate_locale()
            translation.activate(lang)
            request.session[translation.LANGUAGE_SESSION_KEY] = lang
            request.session['django_timezone'] = user.timezone

            return redirect(settings)
        else:
            messages.error(request, _("Error in profile data"))

    return render(request, "accounts/settings.html", locals())


def orders(request):
    """
    This is basically like orders/index, but limited to the user
    First, filter by the provided search criteria,
    then check if we have a saved search filter
    then default to user id
    Always update saved search filter
    """
    args = request.GET.copy()
    default = {'state': Order.STATE_OPEN}

    if len(args) < 2:
        f = request.session.get("account_search_filter", default)
        args = QueryDict('', mutable=True)
        args.update(f)

    # On the profile page, filter by the user, no matter what
    args.update({'followed_by': request.user.pk})
    request.session['account_search_filter'] = args

    data = prepare_list_view(request, args)
    data['title'] = _("My Orders")

    del(data['form'].fields['assigned_to'])

    return render(request, "accounts/orders.html", data)


def login(request):
    """
    User trying to log in
    """
    title = _("Sign In")
    form = LoginForm()

    if 'username' in request.POST:

        form = LoginForm(request.POST)

        if form.is_valid():
            user = auth.authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            if user is None:
                messages.error(request, _("Incorrect username or password"))
            elif not user.is_active:
                messages.error(request, _("Your account has been deactivated"))
            else:
                auth.login(request, user)

                if user.location is not None:
                    lang = user.activate_locale()
                    request.session['django_language'] = lang
                    request.session['django_timezone'] = user.timezone

                messages.success(request, _(u"%s logged in") % user.get_full_name())

                if request.GET.get('next'):
                    return redirect(request.GET['next'])
                else:
                    return redirect(orders)
        else:
            messages.error(request, _("Invalid input for login"))

    return render(request, "accounts/login.html", locals())


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.info(request, _("You have logged out"))

        return redirect(login)

    return render(request, "accounts/logout.html")


@permission_required("servo.add_calendar")
def calendars(request):
    data = {'title': _('Calendars')}
    data['calendars'] = Calendar.objects.filter(user=request.user)

    if data['calendars'].count() > 0:
        cal = data['calendars'][0]
        return redirect(view_calendar, cal.pk)

    return render(request, "accounts/calendars.html", data)


@permission_required("servo.add_calendar")
def prepare_calendar_view(request, pk, view, start_date):
    """
    Prepares a calendar detail view for other views to use
    """
    calendar = get_object_or_404(Calendar, pk=pk)

    if start_date is not None:
        year, month, day = start_date.split("-")
        start_date = date(int(year), int(month), int(day))
    else:
        start_date = timezone.now().date()

    start = start_date
    finish = start_date + relativedelta(days=+1)

    if view == "week":
        start = start_date + relativedelta(day=1)
        finish = start_date + relativedelta(weeks=+1)

    if view == "month":
        start = start_date + relativedelta(day=1)
        finish = start_date + relativedelta(day=1, months=+1, days=-1)

    data = {'title': "%s %s - %s" % (calendar.title, start.strftime("%x"),
                                     finish.strftime("%x"))}

    data['view'] = view
    data['start'] = start
    data['finish'] = finish

    data['next'] = finish + relativedelta(days=+1)
    data['previous'] = start + relativedelta(days=-1)

    data['calendars'] = Calendar.objects.filter(user=request.user)
    data['events'] = calendar.calendarevent_set.filter(
        started_at__range=(start, finish)
    )

    data['calendar'] = calendar
    data['subtitle'] = calendar.subtitle(start, finish)

    return data


@permission_required("servo.add_calendar")
def download_calendar(request, pk, view):
    calendar = get_object_or_404(Calendar, pk=pk)

    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % calendar.title
    writer = csv.writer(response)
    writer.writerow(['START', 'FINISH', 'HOURS', 'NOTES'])

    for e in calendar.calendarevent_set.all():
        writer.writerow([e.started_at, e.finished_at, e.get_hours(), e.notes])

    return response


@permission_required("servo.add_calendar")
def print_calendar(request, pk, view, start_date):
    data = prepare_calendar_view(request, pk, view, start_date)
    calendar = data['calendar']

    data['location'] = request.user.location
    # Don't show unfinished events in the report
    data['events'] = data['events'].exclude(finished_at=None)
    data['subtitle'] = calendar.subtitle(data['start'], data['finish'])
    return render(request, "accounts/print_calendar.html", data)


@permission_required("servo.add_calendar")
def view_calendar(request, pk, view, start_date=None):
    data = prepare_calendar_view(request, pk, view, start_date)
    data['base_url'] = reverse(view_calendar, args=[pk, view])
    return render(request, "accounts/view_calendar.html", data)


@permission_required("servo.delete_calendar")
def delete_calendar(request, pk):
    calendar = get_object_or_404(Calendar, pk=pk)

    if calendar.user != request.user:
        messages.error(request, _("Users can only delete their own calendars!"))

        return redirect(calendars)

    if request.method == "POST":
        calendar.delete()
        messages.success(request, _('Calendar deleted'))
        return redirect(calendars)

    data = {'title': _("Really delete this calendar?")}
    data['action'] = request.path

    return render(request, "accounts/delete_calendar.html", data)


@permission_required("servo.change_calendar")
def edit_calendar(request, pk=None, view="week"):
    from servo.models.calendar import CalendarForm
    calendar = Calendar(user=request.user)

    if pk:
        calendar = get_object_or_404(Calendar, pk=pk)
        if not calendar.user == request.user:
            messages.error(request, _('You can only edit your own calendar'))
            return redirect(calendars)

    if request.method == "POST":
        form = CalendarForm(request.POST, instance=calendar)

        if form.is_valid():
            calendar = form.save()
            messages.success(request, _("Calendar saved"))
            return redirect(view_calendar, calendar.pk, 'week')

    form = CalendarForm(instance=calendar)

    data = {'title': calendar.title}
    data['form'] = form
    data['action'] = request.path

    return render(request, "accounts/calendar_form.html", data)


@permission_required('servo.change_calendar')
def edit_calendar_event(request, cal_pk, pk=None):
    from servo.models.calendar import CalendarEventForm

    calendar = get_object_or_404(Calendar, pk=cal_pk)
    event = CalendarEvent(calendar=calendar)

    if pk:
        event = get_object_or_404(CalendarEvent, pk=pk)
    else:
        event.save()
        messages.success(request, _(u'Calendar event created'))
        return redirect(event.calendar)

    form = CalendarEventForm(instance=event)

    if request.method == 'POST':
        form = CalendarEventForm(request.POST, instance=event)

        if form.is_valid():
            event = form.save()
            messages.success(request, _(u'Event saved'))
            return redirect(event.calendar)

    data = {'title': _(u'Edit Event')}
    data['form'] = form
    data['calendars'] = Calendar.objects.filter(user=request.user)

    return render(request, 'accounts/edit_calendar_event.html', data)


@permission_required("servo.change_calendar")
def finish_calendar_event(request, cal_pk, pk):
    event = get_object_or_404(get_object_or_404, pk=pk)
    event.set_finished()
    messages.success(request, _(u'Calendar event updated'))
    return redirect(view_calendar, cal_pk, 'week')


def delete_calendar_event(request, cal_pk, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)

    if event.calendar.user != request.user:
        messages.error(request, _(u'Users can only delete their own events!'))
        return redirect(calendars)

    if request.method == 'POST':
        event.delete()
        messages.success(request, _('Calendar event deleted'))
        return redirect(event.calendar)

    data = {'title': _(u'Really delete this event?')}
    data['action'] = request.path
    return render(request, 'accounts/delete_calendar_event.html', data)


def register(request):
    """
    New user applying for access
    """
    form = RegistrationForm()
    data = {'title': _("Register")}

    if request.method == 'POST':

        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = User(is_active=False)
            user.email = form.cleaned_data['email']
            user.last_name = form.cleaned_data['last_name']
            user.first_name = form.cleaned_data['first_name']
            user.set_password(form.cleaned_data['password'])
            user.save()

            messages.success(request, _(u'Your registration is now pending approval.'))

            return redirect(login)

    data['form'] = form
    return render(request, 'accounts/register.html', data)


def clear_notifications(request):
    from datetime import datetime
    ts = [int(x) for x in request.GET.get('t').split('/')]
    ts = datetime(*ts, tzinfo=timezone.get_current_timezone())
    notif = request.user.notifications.filter(handled_at=None)
    notif.filter(triggered_at__lt=ts).update(handled_at=timezone.now())
    messages.success(request, _('All notifications cleared'))
    return redirect(request.META['HTTP_REFERER'])


def search(request):
    """
    User searching for something from their homepage
    """
    query = request.GET.get("q")

    if not query or len(query) < 3:
        messages.error(request, _('Search query is too short'))
        return redirect('accounts-list_orders')

    request.session['search_query'] = query

    # Redirect Order ID:s to the order
    try:
        order = Order.objects.get(code__iexact=query)
        return redirect(order)
    except Order.DoesNotExist:
        pass

    kwargs = request.GET.copy()
    kwargs.update({'followed_by': request.user.pk})
    data = prepare_list_view(request, kwargs)

    data['title'] = _("Search results")
    orders = data['queryset']
    data['orders'] = orders.filter(customer__fullname__icontains=query)

    return render(request, "accounts/orders.html", data)


def stats(request):
    from servo.views.stats import prep_view, BasicStatsForm
    data = prep_view(request)
    form = BasicStatsForm(initial=data['initial'])
    if request.method == 'POST':
        form = BasicStatsForm(request.POST, initial=data['initial'])
        if form.is_valid():
            request.session['stats_filter'] = form.cleaned_data
    data['form'] = form
    return render(request, "accounts/stats.html", data)


def updates(request):
    title = _('Updates')
    kind = request.GET.get('kind', 'note_added')
    events = request.user.notifications.filter(action=kind)
    page = request.GET.get("page")
    events = paginate(events, page, 100)

    return render(request, "accounts/updates.html", locals())
