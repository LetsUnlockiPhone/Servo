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

import re
import io

from django import forms
from django import template
from django.utils.translation import ugettext as _
from django.contrib.auth.models import Permission

from servo.forms.base import BaseForm, BaseModelForm
from servo.forms.account import ProfileForm

from servo.models.common import *
from servo.models.queue import *
from servo.models import User, Group, Checklist


class UserUploadForm(forms.Form):
    datafile = forms.FileField()
    location = forms.ModelChoiceField(queryset=Location.objects.all())
    queues = forms.ModelMultipleChoiceField(
        queryset=Queue.objects.all()
    )
    group = forms.ModelChoiceField(queryset=Group.objects.all())
    queues = forms.ModelMultipleChoiceField(
        queryset=Queue.objects.all()
    )

    def save(self, **kwargs):
        users = []
        string = u''
        cd = self.cleaned_data
        data = cd['datafile'].read()

        for i in ('utf-8', 'latin-1',):
            try:
                string = data.decode(i)
            except:
                pass

        if not string:
            raise ValueError(_('Unsupported file encoding'))

        sio = io.StringIO(string, newline=None)

        for l in sio.readlines():
            cols = l.strip().split("\t")
            if len(cols) < 2:
                continue # Skip empty rows

            user = User(username=cols[2])
            user.first_name = cols[0]
            user.last_name = cols[1]
            user.email = cols[3]
            user.set_password(cols[4])
            user.save()

            user.location = cd['location']
            user.timezone = user.location.timezone
            user.groups.add(cd['group'])
            user.queues = cd['queues']
            user.save()

            users.append(user)

        return users


class GsxAccountForm(forms.ModelForm):
    class Meta:
        model = GsxAccount
        exclude = []
        widgets = {'password': forms.PasswordInput}

    def clean(self):
        cd = super(GsxAccountForm, self).clean()
        # Don't save empty passwords
        if cd['password'] == '':
            del cd['password']

        return cd


class GroupForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Group

    user_set = forms.ModelMultipleChoiceField(
        required=False,
        label=_('Group members'),
        queryset=User.active.all(),
        widget=forms.CheckboxSelectMultiple
    )

    permissions = forms.ModelMultipleChoiceField(
        required=False,
        label=_('Permissions'),
        widget=forms.CheckboxSelectMultiple,
        queryset=Permission.objects.filter(content_type__app_label='servo')
    )

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            user_ids = [u.pk for u in self.instance.user_set.all()]
            self.fields['user_set'].initial = user_ids

    def save(self, *args, **kwargs):
        group = super(GroupForm, self).save(*args, **kwargs)
        group.user_set.clear()
        for u in self.cleaned_data['user_set']:
            group.user_set.add(u)
        return group


class ChecklistForm(BaseModelForm):
    class Meta:
        model = Checklist
        exclude = []
        widgets = {'queues': forms.CheckboxSelectMultiple}


class LocationForm(BaseModelForm):
    class Meta:
        model = Location
        exclude = []
        widgets = {'gsx_accounts': forms.CheckboxSelectMultiple}

    def save(self, **kwargs):
        from django.db.utils import IntegrityError

        try:
            location = super(LocationForm, self).save(**kwargs)
        except IntegrityError:
            msg = _('A location with that name already exists')
            self._errors['title'] = self.error_class([msg])
            raise forms.ValidationError(msg)

        return location


class QueueForm(BaseModelForm):

    gsx_soldto = forms.ChoiceField(required=False, choices=())
    users = forms.ModelMultipleChoiceField(queryset=User.active.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    class Meta:
        model = Queue
        exclude = ('statuses',)
        widgets = {
            'description'   : forms.Textarea(attrs={'rows': 4}),
            'keywords'      : forms.Textarea(attrs={'rows': 4}),
            'locations'     : forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super(QueueForm, self).__init__(*args, **kwargs)
        self.fields['gsx_soldto'].choices = GsxAccount.get_soldto_choices()

        if "instance" in kwargs:
            queue = kwargs['instance']
            queryset = QueueStatus.objects.filter(queue=queue)
            self.fields['status_created'].queryset = queryset
            self.fields['status_assigned'].queryset = queryset
            self.fields['status_products_ordered'].queryset = queryset
            self.fields['status_products_received'].queryset = queryset
            self.fields['status_repair_completed'].queryset = queryset
            self.fields['status_dispatched'].queryset = queryset
            self.fields['status_closed'].queryset = queryset


class StatusForm(BaseModelForm):
    class Meta:
        model = Status
        exclude = []
        widgets = {
            'site': forms.HiddenInput,
            'limit_green': forms.TextInput(attrs={'class': 'input-mini'}),
            'limit_yellow': forms.TextInput(attrs={'class': 'input-mini'}),
        }

class UserForm(ProfileForm):
    def clean_username(self):
        reserved = (
            'admin',
            'orders',
            'sales',
            'devices',
            'customers',
            'notes',
            'api',
            'checkin',
            'feedback',
        )
        username = self.cleaned_data.get('username')
        if username in reserved:
            raise forms.ValidationError(_(u'"%s" cannot be used as a username') % username)

        return username

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "is_active",
            "groups",
            "is_staff",
            "location",
            "locations",
            "locale",
            "queues",
            "region",
            "timezone",
            "tech_id",
            "gsx_userid",
            "customer",
            "gsx_poprefix",
        )
        widgets = {
            'locations': forms.CheckboxSelectMultiple,
            'queues': forms.CheckboxSelectMultiple
        }

class TemplateForm(BaseModelForm):
    class Meta:
        model = Template
        exclude = []
        widgets = {
            'title': forms.TextInput(attrs={'class': 'span12'}),
            'content': forms.Textarea(attrs={'class': 'span12'})
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        try:
            template.Template(content)
        except template.TemplateSyntaxError, e:
            raise forms.ValidationError(_('Syntax error in template: %s') % e)

        return content


class SettingsForm(BaseForm):
    # Servo's general System Settings form
    company_name = forms.CharField(label=_('Company Name'))
    company_logo = forms.ImageField(
        label=_('Company Logo'),
        required=False,
        help_text=_('Company-wide logo to use in print templates')
    )

    terms_of_service = forms.CharField(
        required=False,
        label=_('Terms of Service'),
        widget=forms.Textarea(attrs={'class': 'span10'}),
        help_text=_('These terms will be added to your work confirmations and public check-in site.')
    )

    autocomplete_repairs = forms.BooleanField(
        initial=True,
        required=False,
        label=_("Autocomplete GSX repairs"),
        help_text=_("Complete the GSX repair when closing a Service Order")
    )

    # start checkin fields
    checkin_user = forms.ModelChoiceField(
        required=False,
        label=_('User Account'),
        queryset=User.active.all(),
        help_text=_('User account to use for the public check-in service'),
    )
    checkin_group = forms.ModelChoiceField(
        required=False,
        label=_('Group'),
        queryset=Group.objects.all(),
        help_text=_('Users to choose from in the check-in interface'),
    )
    checkin_checklist = forms.ModelChoiceField(
        required=False,
        label=_('Checklist'),
        queryset=Checklist.objects.filter(enabled=True),
        help_text=_('Checklist to show during check-in'),
    )
    checkin_queue = forms.ModelChoiceField(
        required=False,
        label=_('Queue'),
        queryset=Queue.objects.all(),
        help_text=_('Orders created through the check-in interface will go into this queue'),
    )
    checkin_timeline = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Show timeline'),
        help_text=_('Show status timeline on public repair status page'),
    )
    checkin_password = forms.BooleanField(
        initial=False,
        required=False,
        label=_('Show password'),
        help_text=_('Make checkin device password field readable'),
    )
    checkin_report_checklist = forms.BooleanField(
        initial=True,
        required=False,
        label=_('Show checklist results'),
        help_text=_('Show checklist results in order confirmation'),
    )

    checkin_require_password = forms.BooleanField(
        initial=True,
        required=False,
        label=_('Require device password'),
    )
    checkin_require_condition = forms.BooleanField(
        initial=True,
        required=False,
        label=_('Require device condition'),
    )

    # end checkin fields

    currency = forms.ChoiceField(
        label=_('Currency'),
        choices=(
            ('DKK', 'DKK'),
            ('EUR', 'EUR'),
            ('GBP', 'GBP'),
            ('SEK', 'SEK'),
            ('USD', 'USD'),
        ),
        initial='EUR'
    )

    gsx_account = forms.ModelChoiceField(
        required=False,
        label=_('Default GSX account'),
        queryset=GsxAccount.objects.all(),
        help_text=_('Use this GSX account before and order is assigned to a queue')
    )

    pct_margin = forms.CharField(
        required=False,
        max_length=128,
        label=_('Margin %'),
        help_text=_('Default margin for new products')
    )

    pct_vat = forms.DecimalField(
        max_digits=4,
        required=False,
        label=_('VAT %'),
        help_text=_('Default VAT for new products')
    )

    shipping_cost = forms.DecimalField(
        max_digits=4,
        required=False,
        label=_('Shipping Cost'),
        help_text=_('Default shipping cost for new products')
    )

    track_inventory = forms.BooleanField(
        initial=True,
        required=False,
        label=_('Track inventory'),
        help_text=_('Unchecking this will disable tracking product amounts in your inventory')
    )

    imap_host = forms.CharField(
        label=_('IMAP server'),
        max_length=128,
        required=False
    )
    imap_user = forms.CharField(
        label=_('Username'),
        max_length=128,
        required=False
    )
    imap_password = forms.CharField(
        max_length=128,
        label=_('Password'),
        widget=forms.PasswordInput(),
        required=False
    )
    imap_ssl = forms.BooleanField(label=_('Use SSL'), initial=True, required=False)
    imap_act = forms.ModelChoiceField(
        required=False,
        label=_('User Account'),
        queryset=User.active.all(),
        help_text=_('User account to use when creating notes from messages'),
    )

    default_sender = forms.ChoiceField(
        required=False,
        label=_('Default Sender'),
        choices=(
            ('user', _("User")),
            ('location', _("Location")),
            ('custom', _("Custom..."))
        ),
        help_text=_('Select the default sender address for outgoing emails')
    )
    default_sender_custom = forms.EmailField(
        label=' ',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'user@example.com', 'disabled': 'disabled'
        })
    )
    default_subject = forms.CharField(
        max_length=128,
        required=False,
        label=_('Default subject')
    )
    smtp_host = forms.CharField(
        max_length=128,
        required=False,
        label=_('SMTP server')
    )
    smtp_user = forms.CharField(max_length=128, required=False, label=_('Username'))
    smtp_password = forms.CharField(
        max_length=128,
        required=False,
        label=_('Password'),
        widget=forms.PasswordInput()
    )
    smtp_ssl = forms.BooleanField(initial=True, required=False, label=_('Use SSL'))

    sms_gateway = forms.ChoiceField(
        label=_('SMS Gateway'),
        choices=(
            ('builtin', _('Built-in')),
            ('hqsms', 'HQSMS'),
            ('http', 'HTTP'),
            ('smtp', 'SMTP'),
            ('jazz', 'SMSjazz'),
        ),
        initial='http',
        required=False)
    sms_smtp_address = forms.EmailField(required=False, label=_('Email address'))
    sms_http_url = forms.CharField(
        max_length=128,
        label=_('URL'),
        required=False,
        help_text=_('SMS Server URL'),
        initial='http://example.com:13013/cgi-bin/sendsms'
    )
    sms_http_user = forms.CharField(max_length=128, label=_('Username'), required=False)
    sms_http_password = forms.CharField(
        max_length=128,
        required=False,
        label=_('Password'),
        widget=forms.PasswordInput()
    )
    sms_http_sender = forms.CharField(
        max_length=128,
        required=False,
        label=_('Sender')
    )
    sms_http_ssl = forms.BooleanField(
        required=False,
        label=_('Use SSL'),
        initial=True
    )
    notify_location = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Notify locations'),
        help_text=_("Daily reports will be sent to the location's email address")
    )
    notify_address = forms.EmailField(
        required=False,
        label=_('Email address'),
        help_text=_("Send daily reports to this email address")
    )

    def clean_notify_address(self, *args, **kwargs):
        """
        Only validate notify_address if it was actually given
        """
        from django.core.validators import validate_email
        address = self.cleaned_data.get('notify_address')

        if len(address):
            validate_email(address)

        return address

    def clean_pct_margin(self, *args, **kwargs):
        margin = self.cleaned_data.get('pct_margin')
        if re.match('^\d[\-=;\d]*\d$', margin):
            return margin

        raise forms.ValidationError(_('Invalid margin %'))

    def save(self, *args, **kwargs):
        config = dict()

        if self.cleaned_data.get('company_logo'):
            f = self.cleaned_data['company_logo']
            target = 'uploads/logos/%s' % f.name
            with open(target, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            self.cleaned_data['company_logo'] = 'logos/%s' % f.name
        else:
            # @fixme: make the form remember the previous value
            self.cleaned_data['company_logo'] = Configuration.get_company_logo()

        for k, v in self.cleaned_data.items():
            field = Configuration.objects.get_or_create(key=k)[0]

            if re.search('password$', k) and v == '':
                v = field.value  # don't save empty passwords
            if hasattr(v, 'pk'):
                v = v.pk # so we don't end up with object instances in the cache

            field.value = v or ''
            field.save()
            config[k] = v

        cache.set('config', config)

        return config
