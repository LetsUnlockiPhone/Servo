# -*- coding: utf-8 -*-

import json
from django import forms
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class NullCharField(forms.CharField):
    def clean(self, value):
        cleaned = super(NullCharField, self).clean(value)
        return cleaned if len(cleaned) else None


class FullTextArea(forms.CharField):
    widget = forms.Textarea(attrs={'class': 'span12'})


class SearchField(forms.CharField):
    widget = forms.TextInput(attrs={
        'class': 'search-query',
        'autocomplete': 'off',
        'placeholder': '',
    })


class ChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] = 'span12'


class TextInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super(TextInput, self).__init__(*args, **kwargs)
        self.attrs['class'] = 'span12'


class AutocompleteCharField(forms.CharField):
    widget = forms.TextInput(attrs={
        'class'         : "input typeahead",
        'data-provide'  : "typeahead"
        })

    def __init__(self, values, *args, **kwargs):
        super(AutocompleteCharField, self).__init__(*args, **kwargs)

        if not type(values) is str:
            values = json.dumps(list(values))

        self.widget.attrs['data-source'] = values


class AutocompleteTextarea(forms.Textarea):
    def __init__(self, rows=8, choices=None):
        super(AutocompleteTextarea, self).__init__()
        self.attrs = {
            'rows': rows,
            'class': "span12 autocomplete",
            'data-source': json.dumps(choices)
        }


class BaseForm(forms.Form):
    required_css_class = "required"


class BaseModelForm(forms.ModelForm):
    required_css_class = "required"


class SearchFieldInput(forms.TextInput):

    def render(self, name, value, attrs=None):

        field = super(SearchFieldInput, self).render(name, value, attrs)
        final_attrs = self.build_attrs(attrs, name=name)

        output = format_html(u'''
         <div class="input-group">
            {1}
             <span class="input-group-btn">
                <button class="btn btn-default" type="button"><i class="glyphicon glyphicon-search"></i></button>
            </span>
        </div>
        ''', flatatt(final_attrs), field)

        return mark_safe(output)


class DatepickerInput(forms.DateInput):
    def __init__(self, *args, **kwargs):
        kwargs['format'] = "%Y-%m-%d"
        super(DatepickerInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):

        date_format = "yyyy-MM-dd"

        if "format" not in self.attrs:
            attrs['format'] = date_format

        if "data-format" not in self.attrs:
            attrs['data-format'] = date_format

        field = super(DatepickerInput, self).render(name, value, attrs)
        final_attrs = self.build_attrs(attrs, name=name)

        output = format_html(u'''
         <div class="input-append date datepicker" data-provide="datepicker" {0}>
            {1}
            <span class="add-on">
                <i data-time-icon="icon-time" data-date-icon="icon-calendar"></i>
            </span>
        </div>
        ''', flatatt(final_attrs), field)

        return mark_safe(output)


class DateTimePickerInput(forms.DateTimeInput):
    def __init__(self, *args, **kwargs):
        kwargs['format'] = "%Y-%m-%d %H:%M"
        super(DateTimePickerInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):

        date_format = "yyyy-MM-dd hh:mm"

        if "data-format" not in self.attrs:
            attrs['data-format'] = date_format
        if "class" not in self.attrs:
            attrs['class'] = 'input-medium'

        field = super(DateTimePickerInput, self).render(name, value, attrs)
        final_attrs = self.build_attrs(attrs, name=name)

        output = format_html(u'''
         <div class="input-append date datetimepicker" {0}>
            {1}
            <span class="add-on">
                <i data-time-icon="icon-time" data-date-icon="icon-calendar"></i>
            </span>
        </div>
        ''', flatatt(final_attrs), field)

        return mark_safe(output)
