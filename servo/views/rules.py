# -*- coding: utf-8 -*-

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
