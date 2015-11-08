# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    "servo.views.diagnostics",
    url(r'^fetch_url/$', 'fetch_dc_url', name="diagnostics-fetch_url"),
)
