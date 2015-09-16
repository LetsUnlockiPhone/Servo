# -*- coding: utf-8 -*-

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
