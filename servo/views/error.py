# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from servo.lib.shorturl import from_time
from servo.forms.base import FullTextArea
from django.shortcuts import render
from django.utils.translation import ugettext as _


class ErrorForm(forms.Form):
    description = FullTextArea(max_length=512, min_length=10)


def report(request):
    crashed = True
    if request.method == 'POST':
        form = ErrorForm(request.POST)
        if form.is_valid():
            ref = 'Error %s' % from_time()
            recipient = settings.ADMINS[0][1]
            send_mail(ref, form.cleaned_data['description'], request.user.email, [recipient])
            crashed = False
    else:
        initial = _('Browser: %s') % request.META['HTTP_USER_AGENT']
        form = ErrorForm(initial={'description': initial})

    return render(request, 'error.html', locals())
