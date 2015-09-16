# -*- coding: utf-8 -*-

from django import forms
from datetime import timedelta
from django.utils import timezone
from servo.forms import DatepickerInput
from django.utils.translation import ugettext as _

from servo.models import Location, Group, Status, Tag, Queue

default_timescale   = 'WEEK'
default_end_date    = timezone.now()
default_start_date  = default_end_date - timedelta(days=30)


class BasicStatsForm(forms.Form):
    timescale = forms.ChoiceField(
        label=_('Time Scale'),
        choices=(
            ('DAY',     _('Day')),
            ('WEEK',    _('Week')),
            ('MONTH',   _('Month'))
        )
    )
    start_date = forms.DateField(
        label=_('Start date'),
        widget=DatepickerInput(attrs={'class': "input-small"})
    )
    end_date = forms.DateField(
        label=_('End date'),
        widget=DatepickerInput(attrs={'class': "input-small"})
    )

    def serialize(self):
        import datetime
        from django.db.models import Model
        cd = self.cleaned_data

        for k, v in cd.iteritems():
            if isinstance(v, datetime.datetime):
                cd[k] = str(v)
            if isinstance(v, Model):
                cd[k] = v.pk

        return cd


class OrderStatsForm(BasicStatsForm):
    location = forms.ModelChoiceField(
        required=False,
        label=_('Location'),
        queryset=Location.objects.all()
    )


class TechieStatsForm(OrderStatsForm):
    group = forms.ModelChoiceField(
        required=False,
        label=_('Group'),
        queryset=Group.objects.all()
    )


class StatusStatsForm(OrderStatsForm):
    status = forms.ModelChoiceField(
        label=_('Status'),
        queryset=Status.objects.all()
    )


class InvoiceStatsForm(BasicStatsForm):
    pass


class NewStatsForm(forms.Form):
    location = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all()
    )
    queue = forms.ModelMultipleChoiceField(
        queryset=Queue.objects.all(),
        widget=forms.SelectMultiple
    )
    label = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(type="order"),
        required=False
    )
    status = forms.ModelMultipleChoiceField(
        queryset=Status.objects.all(),
        required=False
    )
    start_date = forms.DateField(
        widget=DatepickerInput(attrs={'class': "input-small"}),
        initial=default_start_date
    )
    end_date = forms.DateField(
        widget=DatepickerInput(attrs={'class': "input-small"}),
        initial=default_end_date
    )
