# -*- coding: utf-8 -*-

from django.utils import timezone
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from servo.models.common import Event


def acknowledge(request, pk):
    e = Event.objects.get(pk=pk)
    e.handled_at = timezone.now()
    e.save()

    referer = request.META.get('HTTP_REFERER')

    if request.GET.get('return') == '0'and referer:
        return redirect(referer)

    return redirect(e.content_object.get_absolute_url())
