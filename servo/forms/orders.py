# -*- coding: utf-8 -*-

import gsxws

from django import forms
from django.utils.translation import ugettext as _

from django.utils.safestring import mark_safe

from servo.models.parts import symptom_codes
from servo.models import Location, Queue, Status, Tag
from servo.models import User, Invoice, Payment

from servo.models.order import *
from servo.forms.base import *


class BatchProcessForm(forms.Form):
    orders = forms.CharField(
        widget=forms.Textarea,
        label=_('Service order(s)')
    )

    status = forms.ModelChoiceField(
        required=False,
        label=_('Set status to'),
        queryset=Status.objects.all()
    )
    queue = forms.ModelChoiceField(
        required=False,
        label=_('Set queue to'),
        queryset=Queue.objects.all()
    )
    sms = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label=_('Send SMS to customer')
    )
    email = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label=_('Send E-mail to customer')
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label=_('Add note to order')
    )


class FieldsForm(forms.Form):
    pass


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = ServiceOrderItem
        fields = ('title', 'amount', 'price_category',
                  'price', 'sn', 'kbb_sn', 'imei', 'should_report',
                  'comptia_code', 'comptia_modifier',)
        widgets = {
            'amount': forms.TextInput(attrs={'class': 'input-mini'}),
            'price': forms.TextInput(attrs={'class': 'input-mini'})
        }

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)

        if self.instance:
            product = self.instance.product
            if product.can_order_from_gsx():
                CODES = symptom_codes(product.component_code)
                self.fields['comptia_code'] = forms.ChoiceField(choices=CODES)
                self.fields['comptia_modifier'] = forms.ChoiceField(
                    choices=gsxws.MODIFIERS,
                    initial="B"
                )


class OrderSearchForm(forms.Form):
    """
    Form for searching Service Orders
    """
    checkin_location = forms.ModelMultipleChoiceField(
        required=False,
        label=_("Checked in at"),
        queryset=Location.objects.all(),
    )
    location = forms.ModelMultipleChoiceField(
        required=False,
        label=_("Location is"),
        queryset=Location.objects.filter(enabled=True),
    )
    state = forms.MultipleChoiceField(
        required=False,
        label=_("State is"),
        choices=Order.STATES,
    )
    queue = forms.ModelMultipleChoiceField(
        required=False,
        label=_("Queue is"),
        queryset=Queue.objects.all(),
    )
    status = forms.ModelMultipleChoiceField(
        required=False,
        label=_("Status"),
        queryset=Status.objects.all(),
    )
    created_by = forms.ModelMultipleChoiceField(
        required=False,
        label=_("Created by"),
        queryset=User.active.all(),
    )
    assigned_to = forms.ModelMultipleChoiceField(
        required=False,
        label=_("Assigned to"),
        queryset=User.active.all(),
    )
    label = forms.ModelMultipleChoiceField(
        required=False,
        label=_("Label"),
        queryset=Tag.objects.filter(type="order"),
    )
    color = forms.MultipleChoiceField(
        choices=(
            ('green',   _("Green")),
            ('yellow',  _("Yellow")),
            ('red',     _("Red")),
            ('grey',    _("Grey")),
        ),
        label=_("Color"),
        required=False,
    )
    start_date = forms.DateField(
        required=False,
        label=_("Created between"),
        widget=DatepickerInput(attrs={'class': "input-small"})
    )
    end_date = forms.DateField(
        required=False,
        label=mark_safe('&nbsp;'),
        widget=DatepickerInput(attrs={'class': "input-small"})
    )
    status_older_than = forms.IntegerField(
        required=False,
        label=_('Status older than (days)'),
    )

    def __init__(self, request, *args, **kwargs):
        super(OrderSearchForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = request.user.locations.all()
