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
from django.utils.translation import ugettext as _

from servo.forms import DatepickerInput, NullCharField
from servo.models import Invoice, Payment, Status


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = []
        widgets = {
            'created_by': forms.HiddenInput,
            'method': forms.Select(attrs={'class': 'input-medium'}),
            'amount': forms.NumberInput(attrs={'class': 'input-small'})
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        exclude = []
        widgets = {
            'total_net'         : forms.TextInput(attrs={'class': 'input-small'}),
            'total_tax'         : forms.TextInput(attrs={'class': 'input-small'}),
            'total_gross'       : forms.TextInput(attrs={'class': 'input-small'}),
            'customer_name'     : forms.TextInput(attrs={'class': 'span12'}),
            'customer_email'    : forms.TextInput(attrs={'class': 'span12'}),
            'customer_phone'    : forms.TextInput(attrs={'class': 'span12'}),
            'customer_address'  : forms.TextInput(attrs={'class': 'span12'}),
            'reference'         : forms.TextInput(attrs={'class': 'span12'}),
        }
        localized_fields = ('total_net', 'total_tax', 'total_gross')


class InvoiceSearchForm(forms.Form):
    state = forms.ChoiceField(
        required=False,
        label=_('State is'),
        choices=(
            ('', _('Any')),
            ('OPEN', _('Open')),
            ('PAID', _('Paid')),
        ),
        widget=forms.Select(attrs={'class': 'input-small'})
    )
    payment_method = forms.ChoiceField(
        required=False,
        label=_('Payment method is'),
        choices=(('', _('Any')),) + Payment.METHODS,
        widget=forms.Select(attrs={'class': 'input-medium'})
    )
    status_isnot = forms.ModelChoiceField(
        required=False,
        label=_('Status is not'),
        queryset=Status.objects.all(),
        widget=forms.Select(attrs={'class': 'input-medium'})
    )
    start_date = forms.DateField(
        required=False,
        label=_('Start date'),
        widget=DatepickerInput(attrs={
            'class': "input-small",
            'placeholder': _('Start date')
        })
    )
    end_date = forms.DateField(
        required=False,
        label=_('End date'),
        widget=DatepickerInput(attrs={
            'class': "input-small",
            'placeholder': _('End date')
        })
    )
    customer_name = NullCharField(
        required=False,
        label=_('Customer name contains')
    )
    service_order = NullCharField(
        required=False,
        label=_('Service Order is')
    )
