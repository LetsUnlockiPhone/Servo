# -*- coding: utf-8 -*-

from django.conf.urls import url

from servo.views.stats import *


urlpatterns = [
    url(r'^$', index, name="stats-index"),
    url(r'^sales/$', sales, name="stats-sales"),
    url(r'^queues/$', queues, name="stats-queues"),
    url(r'^locations/$', locations, name="stats-locations"),
    url(r'^statuses/$', statuses, name="stats-statuses"),
    url(r'^data/(?P<query>[\w/\-]+)/$', data, name="stats-data"),
    url(r'^repairs/$', repairs, name="stats-repairs"),
    url(r'^devices/$', devices, name="stats-devices"),
]
