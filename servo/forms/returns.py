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

import gsxws
from django import forms
from django.utils.translation import ugettext as _

from servo.models import Location, Shipment, ServicePart


class ConvertToStockForm(forms.Form):
    partNumber = forms.CharField(widget=forms.HiddenInput())


class GoodPartReturnForm(forms.Form):
    comptiaModifier = forms.ChoiceField(
        label=_("Reason"),
        choices=[
            ('', _("Select...")),
            ('A', _("Part not needed")),
            ('B', _("Duplicated part")),
            ('C', _("Added wrong part")),
            ('D', _("Tried to cancel order")),
            ('E', _("Customer refused order")),
        ]
    )
    comptiaCode = forms.ChoiceField(
        label=_("Type"),
        choices=[
            ('', _("Select...")),
            ('DIA', _("Diagnostic")),
            ('UOP', _("Un-Opened")),
        ]
    )


class DoaPartReturnForm(forms.Form):
    comptiaCode = forms.ChoiceField(
        label=_("Symptom Code"),
        choices=[('', _("Select..."))]
    )
    comptiaModifier = forms.ChoiceField(
        label=_("Symptom Modifier"),
        choices=gsxws.comptia.MODIFIERS
    )

    def __init__(self, part, data=None):
        super(DoaPartReturnForm, self).__init__(data=data)
        self.fields['comptiaCode'].choices += part.get_comptia_symptoms()


class BulkReturnSearchForm(forms.Form):
    location = forms.ModelChoiceField(
        label=_('Location'),
        queryset=Location.objects.all()
    )


class BulkReturnPartForm(forms.ModelForm):
    class Meta:
        model = ServicePart
        widgets = {
            'box_number': forms.Select(attrs={'class': 'input-small'}),
            'part_number': forms.HiddenInput(),
            'part_title': forms.HiddenInput(),
            'service_order': forms.HiddenInput(),
            'return_order': forms.HiddenInput(),
        }
        exclude = []

    def __init__(self, *args, **kwargs):
        super(BulkReturnPartForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            box_choices = [(0, 'Individual',)]
            instance = kwargs['instance']
            # @TODO: This seems like a totally unnecessary hack...
            # Why can't I just pass the number of options directly to the form?
            part_count = instance.shipment.servicepart_set.all().count()
            for x in xrange(1, part_count):
                box_choices.append((x, x,))

            self.fields['box_number'].widget.choices = box_choices


class BulkReturnForm(forms.ModelForm):
    class Meta:
        model = Shipment
        exclude = []

