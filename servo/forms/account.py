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
from django.utils.translation import ugettext as _

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
