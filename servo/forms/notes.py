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
from gsxws import escalations
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from servo.models import Note, Escalation, Template
from servo.forms import BaseModelForm, AutocompleteTextarea, TextInput


class NoteForm(BaseModelForm):
    class Meta:
        model = Note
        exclude = []
        widgets = {
            'recipient' : TextInput,
            'labels'    : forms.CheckboxSelectMultiple,
            'order'     : forms.HiddenInput,
            'parent'    : forms.HiddenInput,
            'customer'  : forms.HiddenInput,
            'subject'   : TextInput
        }

    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        note = kwargs['instance']
        self.fields['sender'] = forms.ChoiceField(
            label=_('From'),
            choices=note.get_sender_choices(),
            widget=forms.Select(attrs={'class': 'span12'})
        )
        self.fields['body'].widget = AutocompleteTextarea(
            rows=20,
            choices=Template.templates()
        )


class NoteSearchForm(forms.Form):
    body = forms.CharField(required=False, label=_('Body contains'))
    recipient = forms.CharField(required=False, label=_('Recipient contains'))
    sender = forms.CharField(required=False, label=_('Sender contains'))
    order_code = forms.CharField(required=False, label=_('Service Order is'))


class EscalationForm(BaseModelForm):
    keys = forms.CharField(required=False)
    values = forms.CharField(required=False)

    def clean(self):
        contexts = dict()
        cd = super(EscalationForm, self).clean()
        keys = self.data.getlist('keys')
        values = self.data.getlist('values')
        for k, v in enumerate(values):
            if v != '':
                key = keys[k]
                contexts[key] = v

        cd['contexts'] = json.dumps(contexts)
        return cd

    class Meta:
        model = Escalation
        fields = ('issue_type', 'status', 'gsx_account', 'contexts',)

