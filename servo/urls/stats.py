# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'servo.views.stats',
    url(r'^$', 'index', name="stats-index"),
    url(r'^sales/$', 'sales', name="stats-sales"),
    url(r'^queues/$', 'queues', name="stats-queues"),
    url(r'^locations/$', 'locations', name="stats-locations"),
    url(r'^statuses/$', 'statuses', name="stats-statuses"),
    url(r'^data/(?P<query>[\w/\-]+)/$', 'data', name="stats-data"),

    url(r'^repairs/$', 'repairs', name="stats-repairs"),
)
