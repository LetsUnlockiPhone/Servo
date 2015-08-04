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

