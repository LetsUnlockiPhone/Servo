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

import json

from django import forms
from django_countries import countries

from django.utils.translation import ugettext as _

from servo.models import User, Repair, Template
from servo.forms import BaseForm, AutocompleteTextarea, DateTimePickerInput, ChoiceField


class GsxCustomerForm(BaseForm):
    firstName = forms.CharField(max_length=100, label=_('First name'))
    lastName = forms.CharField(max_length=100, label=_('Last name'))
    emailAddress = forms.CharField(max_length=100, label=_('Email'))
    primaryPhone = forms.CharField(max_length=100, label=_('Phone'))
    addressLine1 = forms.CharField(max_length=100, label=_('Address'))
    zipCode = forms.CharField(max_length=100, label=_('ZIP Code'))
    city = forms.CharField(max_length=100, label=_('City'))
    country = ChoiceField(label=_('Country'), choices=countries)
    state = ChoiceField(choices=(('ZZ', _('Other')),), initial="ZZ")


class GsxComponentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        components = kwargs.get('components')
        del kwargs['components']
        super(GsxComponentForm, self).__init__(*args, **kwargs)
        if len(components):
            components = json.loads(components)
            for k, v in components.items():
                self.fields[k] = forms.CharField(label=k, required=True, initial=v)

    def clean(self, *args, **kwargs):
        super(GsxComponentForm, self).clean(*args, **kwargs)
        self.json_data = json.dumps(self.cleaned_data)


class GsxRepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        exclude = []
        widgets = {
            'device' : forms.HiddenInput(),
            'parts': forms.CheckboxSelectMultiple(),
            'unit_received_at': DateTimePickerInput(attrs={'readonly': 'readonly'})
        }

    def __init__(self, *args, **kwargs):
        super(GsxRepairForm, self).__init__(*args, **kwargs)
        repair = kwargs['instance']
        techs = User.techies.filter(location=repair.order.location)
        c = [(u.tech_id, u.get_full_name()) for u in techs]
        c.insert(0, ('', '-------------------',))
        self.fields['tech_id'] = forms.ChoiceField(choices=c,
                                                   required=False,
                                                   label=_('Technician'))
        self.fields['parts'].initial = repair.order.get_parts()

        if not repair.can_mark_complete:
            del self.fields['mark_complete']
            del self.fields['replacement_sn']

        choices = Template.templates()
        for f in ('notes', 'symptom', 'diagnosis'):
            self.fields[f].widget = AutocompleteTextarea(choices=choices)

    def clean(self, *args, **kwargs):
        cd = super(GsxRepairForm, self).clean(*args, **kwargs)
        if self.instance.has_serialized_parts():
            if cd.get('mark_complete') and not cd.get('replacement_sn'):
                raise forms.ValidationError(_('Replacement serial number must be set'))
        return cd
