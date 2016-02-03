# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView

from servo.views.account import *


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='orders', permanent=False)),

    url(r'^search/$', search, name="accounts-search"),
    url(r'^orders/$', orders, name="accounts-list_orders"),
    url(r'^settings/$', settings, name="accounts-settings"),
    url(r'^stats/$', stats, name="accounts-stats"),
    url(r'^updates/$', updates, name="accounts-updates"),

    url(r'^calendars/$', calendars, name="calendars-list"),
    url(r'^calendars/new/$', edit_calendar, name="calendars-create"),
    url(r'^calendars/(?P<pk>\d+)/$', view_calendar, {'view': 'week'},
        name='calendars.view'),

    url(r'^calendars/(?P<pk>\d+)/delete/$', delete_calendar, name='calendars-delete'),

    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/$', view_calendar,
        name='calendars.view'),
    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/(?P<start_date>[0-9\-]+)/$', view_calendar,
        name='calendars-view_calendar'),
    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/download/$', download_calendar,
        name='calendars-download'),
    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/(?P<start_date>[0-9\-]+)/print/$', print_calendar,
        name="calendars-print"),
    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/edit/$', edit_calendar,
        name='calendars-edit'),

    url(r'^calendars/(?P<cal_pk>\d+)/events/new/$', edit_calendar_event,
        name='calendars.event.edit'),
    url(r'^calendars/(?P<cal_pk>\d+)/events/(?P<pk>\d+)/edit/$', edit_calendar_event,
        name='calendars.event.edit'),
    url(r'^calendars/(?P<cal_pk>\d+)/events/(?P<pk>\d+)/delete/$', delete_calendar_event,
        name='calendars.event.delete'),
    url(r'^calendars/(?P<cal_pk>\d+)/events/(?P<pk>\d+)/finish/$', finish_calendar_event,
        name='calendars.event.finish'),

    url(r'^notifications/clear/$', clear_notifications, name="accounts-clear_notifications"),
]
