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

import phonenumbers
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from servo.forms.base import BaseModelForm, DatepickerInput
from servo.models import Customer


class CustomerForm(BaseModelForm):
    class Meta:
        model = Customer
        widgets = {
            'groups': forms.CheckboxSelectMultiple
        }
        exclude = []

    def clean_name(self):
        name = self.cleaned_data.get('name')
        return name.strip()

    def clean(self):
        cd = super(CustomerForm, self).clean()

        phone = cd.get('phone')
        country = cd.get('country')

        if len(phone) < 1:
            return cd

        try:
            phonenumbers.parse(phone, country)
        except phonenumbers.NumberParseException:
            msg = _('Enter a valid phone number')
            self._errors["phone"] = self.error_class([msg])

        return cd


class CustomerSearchForm(forms.Form):
    name__icontains = forms.CharField(
        required=False,
        label=_('Name contains')
    )
    email__icontains = forms.CharField(
        required=False,
        label=_('Email contains')
    )
    street_address__icontains = forms.CharField(
        required=False,
        label=_('Address contains')
    )
    checked_in_start = forms.DateField(
        required=False,
        label=_('Checked in between'),
        widget=DatepickerInput(attrs={'class': "input-small"})
    )
    checked_in_end = forms.DateField(
        required=False,
        label=mark_safe('&nbsp;'),
        widget=DatepickerInput(attrs={'class': "input-small"})
    )

    def clean(self):
        cd = super(CustomerSearchForm, self).clean()

        for k, v in cd.items():
            if v not in ['', None]:
                return cd

        raise forms.ValidationError(_('Please specify at least one parameter'))


class CustomerUploadForm(forms.Form):
    datafile = forms.FileField(label=_('CSV file'))
    skip_dups = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Skip duplicates'),
        help_text=_('Skip customers with existing email addresses')
    )

    def clean_datafile(self):
        d = self.cleaned_data.get('datafile')
        if not d.content_type.startswith('text'):
            raise forms.ValidationError(_('Data file should be in text format'))
        return d
