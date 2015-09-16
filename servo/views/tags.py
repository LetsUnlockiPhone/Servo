# -*- coding: utf-8 -*-

from django.http import HttpResponse
from servo.models import TaggedItem


def clear(request, pk):
    TaggedItem.objects.get(pk=pk).delete()
    return HttpResponse("")


def add(request, content_type, pk, tag):
    pass
