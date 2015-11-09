# -*- coding: utf-8 -*-

import math

from dateutil.rrule import DAILY, rrule

from django import forms
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum


class Calendar(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        editable=False
    )

    title = models.CharField(
        max_length=128,
        verbose_name=_('title'),
        default=_('New Calendar')
    )
    hours_per_day = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Hours per day"),
        help_text=_("How many hours per day should be in this calendar")
    )

    def min_hours(self):
        return self.hours_per_day or 0

    def get_overtime(self, total_hours, workdays):
        overtime = total_hours - (self.min_hours() * workdays)
        return overtime if overtime > 0 else 0

    def subtitle(self, start_date, end_date):
        workdays = self.get_workdays(start_date, end_date)
        total_hours = self.get_total_hours(start_date, end_date)
        overtime = self.get_overtime(total_hours, workdays)

        if overtime > 1:
            d = {'hours': total_hours, 'workdays': workdays, 'overtime': overtime}
            subtitle = _("%(hours)s hours total in %(workdays)s days (%(overtime)s hours overtime)." % d)
        else:
            d = {'hours': total_hours, 'workdays': workdays}
            subtitle = _("%(hours)s hours total in %(workdays)s days." % d)

        return subtitle

    def get_workdays(self, start_date, end_date):
        WORKDAYS = xrange(0, 5)
        r = rrule(DAILY, dtstart=start_date, until=end_date, byweekday=WORKDAYS)
        return r.count()

    def get_unfinished_count(self):
        count = self.calendarevent_set.filter(finished_at=None).count()
        return count or ""

    def get_total_hours(self, start=None, finish=None):
        """
        Returns in hours, the total duration of events in this calendar within
        a time period.
        """
        events = self.calendarevent_set.all()

        if start and finish:
            events = self.calendarevent_set.filter(started_at__range=(start, finish))

        total = events.aggregate(total=Sum('seconds'))['total'] or 0

        return math.ceil(total/3600.0)

    def get_absolute_url(self):
        return reverse('calendars.view', args=[self.pk])

    class Meta:
        app_label = "servo"


class CalendarEvent(models.Model):

    calendar = models.ForeignKey(
        Calendar,
        editable=False
    )

    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)

    # The duration of this event in seconds
    seconds = models.PositiveIntegerField(
        null=True,
        editable=False
    )

    notes = models.TextField(null=True, blank=True)

    def get_start_date(self):
        return self.started_at.strftime('%x')

    def get_start_time(self):
        return self.started_at.strftime('%H:%M')

    def get_finish_time(self):
        try:
            return self.finished_at.strftime('%H:%M')
        except AttributeError:
            return ''

    def set_finished(self, ts=timezone.now):
        self.finished_at = ts()
        self.save()

    def get_hours(self):
        return self.seconds/3600.0

    def get_duration(self):
        if self.finished_at is None:
            return ''

        delta = (self.finished_at - self.started_at)
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return '%d:%d' % (hours, minutes)

    def get_absolute_url(self):
        return '/%s/calendars/%d/events/%d' % (self.calendar.user.username, self.calendar.pk, self.pk)

    def save(self, *args, **kwargs):
        self.seconds = 0

        if self.finished_at:
            delta = self.finished_at - self.started_at
            self.seconds = delta.seconds

        super(CalendarEvent, self).save(*args, **kwargs)

    class Meta:
        app_label = 'servo'
        ordering = ['-started_at']


class CalendarForm(forms.ModelForm):
    class Meta:
        model = Calendar
        exclude = []


class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        exclude = []
        