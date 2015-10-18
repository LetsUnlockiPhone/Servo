# -*- coding: utf-8 -*-

import json
from django import forms
from gsxws import escalations
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from servo.models import Note, Escalation, Template
from servo.forms import BaseModelForm, AutocompleteTextarea, TextInput


class NoteForm(BaseModelForm):
    class Meta:
        model = Note
        exclude = []
        widgets = {
            'recipient' : TextInput,
            'subject'   : TextInput,
            'order'     : forms.HiddenInput,
            'parent'    : forms.HiddenInput,
            'customer'  : forms.HiddenInput,
            'type'      : forms.HiddenInput,
            'labels'    : forms.CheckboxSelectMultiple,
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

        if note.order:
            url = reverse('notes-render_template', args=[note.order.pk])
            self.fields['body'].widget.attrs['data-url'] = url


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

