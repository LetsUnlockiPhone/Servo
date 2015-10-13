# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from servo.forms.base import BaseForm, BaseModelForm
from servo.models.account import User


class ProfileForm(BaseModelForm):
    # User Profile form for users
    class Meta:
        model = User
        fields = (
            "location",
            "photo",
            "locale",
            "queues",
            "region",
            "timezone",
            "should_notify",
            "notify_by_email",
            "autoprint",
            "tech_id",
            "gsx_userid",
            "gsx_poprefix",
        )
        widgets = {
            'queues': forms.CheckboxSelectMultiple
        }
        
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label=_("Password")
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label=_("Confirmation")
    )

    def clean(self):
        cd = super(ProfileForm, self).clean()

        if cd.get('gsx_password') == "":
            del cd['gsx_password']

        cd['tech_id'] = cd['tech_id'].upper()

        if cd.get('password1'):
            if cd['password1'] != cd['password2']:
                raise forms.ValidationError(_("Password and confirmation do not match!"))

        return cd

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and photo.size > 1*1024*1024:
            raise forms.ValidationError(_('File size of photo is too large'))

        return photo


class RegistrationForm(BaseForm):
    first_name = forms.CharField(label=_("First Name"))
    last_name = forms.CharField(label=_("Last Name"))
    email = forms.EmailField(label=_("Email Address"))
    password = forms.CharField(widget=forms.PasswordInput, label=_("Password"))


class LoginForm(BaseForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Username')})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': _('Password')})
    )
