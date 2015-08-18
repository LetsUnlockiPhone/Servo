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
