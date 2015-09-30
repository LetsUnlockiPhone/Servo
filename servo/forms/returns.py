# -*- coding: utf-8 -*-

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
            'box_number'   : forms.Select(attrs={'class': 'input-small'}),
            'part_number'  : forms.HiddenInput(),
            'part_title'   : forms.HiddenInput(),
            'service_order': forms.HiddenInput(),
            'return_order' : forms.HiddenInput(),
        }
        exclude = []

    def __init__(self, *args, **kwargs):
        super(BulkReturnPartForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            box_choices = [(0, 'Individual',)]
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

