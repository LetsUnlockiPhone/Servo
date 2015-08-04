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

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect, get_object_or_404

from servo.models.rules import *


def get_data(request):
    pass


def list_rules(request):
    title = _('Rules')
    object_list = Rule.objects.all()
    return render(request, "rules/list_rules.html", locals())


def edit_rule(request, pk=None):
    title = _('Rules')
    object_list = Rule.objects.all()

    if pk:
        rule = get_object_or_404(Rule, pk=pk)

    if request.method == 'POST':
        if pk:
            rule = Rule.objects.get(pk=pk)
        else:
            rule = Rule()

        rule.description = request.POST.get('description')
        #rule.match = request.POST.get('description')
        rule.save()

        rule.condition_set.all().delete()
        rule.action_set.all().delete()

        keys = request.POST.getlist('condition-key')
        values = request.POST.getlist('condition-value')

        for k, v in enumerate(keys):
            cond = Condition(rule=rule)
            cond.key = v
            cond.value = values[k]
            cond.save()

        keys = request.POST.getlist('action-key')
        values = request.POST.getlist('action-value')

        for k, v in enumerate(keys):
            action = Action(rule=rule)
            action.key = v
            action.value = values[k]
            action.save()

            
    return render(request, "rules/form.html", locals())


def view_rule(request, pk):
    pass


def delete_rule(request, pk):
    action = request.path
    title = _('Delete rule')
    rule = get_object_or_404(Rule, pk=pk)

    if request.method == 'POST':
        rule.delete()
        messages.error(request, _('Rule deleted'))
        return redirect(list_rules)

    return render(request, "generic/delete.html", locals())
