# -*- coding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from servo.models import Tag, Device, Customer
from servo.forms import DatepickerInput, AutocompleteCharField

product_lines = [(k, x['name']) for k, x in Device.PRODUCT_LINES.items()]


class DeviceSearchForm(forms.Form):
    product_line = forms.MultipleChoiceField(
        #widget=forms.CheckboxSelectMultiple,
        choices=product_lines,
        required=False
    )
    warranty_status = forms.MultipleChoiceField(
        #widget=forms.CheckboxSelectMultiple,
        choices=Device.WARRANTY_CHOICES,
        required=False,
    )
    date_start = forms.DateField(
        required=False,
        label=_('Created between'),
        widget=DatepickerInput(attrs={'class': 'input-small'})
    )
    date_end = forms.DateField(
        required=False,
        label=mark_safe('&nbsp;'),
        widget=DatepickerInput(attrs={'class': 'input-small'})
    )
    sn = forms.CharField(required=False, label=_('Serial number contains'))
    
    def __init__(self, *args, **kwargs):
        super(DeviceSearchForm, self).__init__(*args, **kwargs)
        self.fields['description'] = AutocompleteCharField(
            '/api/device_models/',
            max_length=128,
            required=False,
            label=_('Description contains')
        )


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        exclude = ('spec', 'customers', 'files', 'image_url',
                   'exploded_view_url', 'manual_url',)
        widgets = {'purchased_on': DatepickerInput()}

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.filter(type='device'),
        required=False
    )


class DeviceUploadForm(forms.Form):
    datafile = forms.FileField()
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False
    )
    do_warranty_check = forms.BooleanField(required=False, initial=True)


class DiagnosticsForm(forms.Form):
    pass

