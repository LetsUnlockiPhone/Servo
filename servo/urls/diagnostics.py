# -*- coding: utf-8 -*-

from django.conf.urls import url

from servo.views.diagnostics import *

urlpatterns = [
    url(r'^fetch_url/$', fetch_dc_url, name="diagnostics-fetch_url"),
]
