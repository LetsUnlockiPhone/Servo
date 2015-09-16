# -*- coding: utf-8 -*-

from django import forms
from servo.models import Queue
from django.http import HttpResponse


def statuses(request, queue_id):
    """Lists available statuses for this queue"""
    queue = Queue.objects.get(pk=queue_id)
    
    class StatusForm(forms.Form):
        status = forms.ModelChoiceField(queryset=queue.queuestatus_set.all())

    form = StatusForm()
    return HttpResponse(str(form['status']))
