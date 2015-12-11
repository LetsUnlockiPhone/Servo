# -*- coding: utf-8 -*-

import re
from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from servo.models import Location, User, TaggedItem
from servo.models.purchases import PurchaseOrderItem
from servo.models.product import Product, ProductCategory, Inventory
from servo.forms.base import BaseModelForm, DatepickerInput, TextInput


class ProductSearchForm(forms.Form):
    title = forms.CharField(required=False, label=_('Name contains'))
    code = forms.CharField(required=False, label=_('Code contains'))
    description = forms.CharField(
        required=False,
        label=_('Description contains')
    )
    tag = forms.ModelChoiceField(
        required=False,
        label=_('Device model is'),
        queryset=TaggedItem.objects.none()
    )
    location = forms.ModelChoiceField(
        required=False,
        label=_('Location is'),
        queryset=Location.objects.filter(enabled=True)
    )

    def __init__(self, *args, **kwargs):
        super(ProductSearchForm, self).__init__(*args, **kwargs)
        tags = TaggedItem.objects.filter(content_type__model="product").distinct("tag")
        self.fields['tag'].queryset = tags


class ProductUploadForm(forms.Form):
    datafile = forms.FileField(label=_("Product datafile"))
    category = forms.ModelChoiceField(
        required=False,
        queryset=ProductCategory.objects.all()
    )


class PartsImportForm(forms.Form):
    partsdb = forms.FileField(label=_("Parts database file"))
    import_vintage = forms.BooleanField(
        initial=True,
        required=False,
        label=_("Import vintage parts")
    )
    update_prices = forms.BooleanField(
        initial=True,
        required=False,
        label=_("Update product prices")
    )


class PurchaseOrderItemEditForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        exclude = ('sn',)
        widgets = {
            'product': forms.HiddenInput(),
            'code': forms.TextInput(attrs={'class': 'input-small'}),
            'amount': forms.TextInput(attrs={'class': 'input-mini'}),
            'price': forms.TextInput(attrs={'class': 'input-mini'}),
            'title': forms.TextInput(attrs={'class': 'input-xlarge'}),
        }
        localized_fields = ('price',)


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ('sn', 'amount',)
        localized_fields = ('price',)

    def clean(self):
        cleaned_data = super(PurchaseOrderItemForm, self).clean()
        return cleaned_data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('files',)
        widgets = {
            'code': TextInput(),
            'title': TextInput(attrs={'class': 'input-xlarge'}),
            'categories': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'class': 'span12', 'rows': 6}),
        }
        localized_fields = (
            'price_purchase_exchange',
            'pct_margin_exchange',
            'price_notax_exchange',
            'price_sales_exchange',
            'price_purchase_stock',
            'pct_margin_stock',
            'price_notax_stock',
            'price_sales_stock',
            'pct_vat',
            'shipping',
        )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not re.match(r'^[\w\-/]+$', code):
            msg = _('Product code %s contains invalid characters') % code
            raise ValidationError(msg)

        return code


class CategoryForm(BaseModelForm):
    class Meta:
        model = ProductCategory
        exclude = []


class PurchaseOrderSearchForm(forms.Form):
    state = forms.ChoiceField(
        required=False,
        label=_('State is'),
        choices=(
            ('',            _('Any')),
            ('open',        _('Open')),
            ('submitted',   _('Submitted')),
            ('received',    _('Received')),
        ),
        widget=forms.Select(attrs={'class': 'input-small'})
    )
    created_by = forms.ModelChoiceField(
        required=False,
        queryset=User.active.all()
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
    reference = forms.CharField(
        required=False,
        label=_('Reference contains')
    )


class IncomingSearchForm(forms.Form):
    """
    A form for searching incoming products
    """
    location = forms.ModelChoiceField(
        label=_('Location is'),
        queryset=Location.objects.all(),
        widget=forms.Select(attrs={'class': 'input-medium'})
    )
    ordered_start_date = forms.DateField(
        label=_('Ordered between'),
        widget=DatepickerInput(attrs={
            'class': "input-small",
            'placeholder': _('Start date')
        })
    )
    ordered_end_date = forms.DateField(
        label='',
        widget=DatepickerInput(attrs={
            'class': "input-small",
            'placeholder': _('End date')
        })
    )
    received_start_date = forms.DateField(
        label=_('Received between'),
        widget=DatepickerInput(attrs={
            'class': "input-small",
            'placeholder': _('Start date')
        })
    )
    received_end_date = forms.DateField(
        label='',
        widget=DatepickerInput(attrs={
            'class': "input-small",
            'placeholder': _('End date')
        })
    )
    confirmation = forms.CharField(
        label=_('Confirmation is')
    )
    service_order = forms.CharField(
        label=_('Service order is')
    )


class ReserveProductForm(forms.Form):
    """
    Form for reserving products for a given SO
    """
    inventory = forms.ModelChoiceField(queryset=Inventory.objects.none(),
                                       label=_('Inventory'))

    def __init__(self, order, *args, **kwargs):
        super(ReserveProductForm, self).__init__(*args, **kwargs)
        inventory = Inventory.objects.filter(location=order.location,
                                             product__in=order.products.all())
        self.fields['inventory'].queryset = inventory


class UploadPricesForm(forms.Form):
    datafile = forms.FileField(label=_('Price data in Excel format (.xlsx)'),
                               help_text=_('This will also update products with fixed prices'))
    create_new = forms.BooleanField(label=_('Create new products'),
                                    required=False,
                                    initial=True,
                                    help_text=_('Create products if not found'))
    set_fixed = forms.BooleanField(label=_('Set fixed price'),
                                   required=False,
                                   help_text=_('Mark all uploaded products as having a fixed price'))
