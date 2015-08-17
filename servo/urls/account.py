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

from django.conf.urls import patterns, url
from django.views.generic import RedirectView

urlpatterns = patterns(
    "servo.views.account",

    url(r'^$', RedirectView.as_view(url='orders', permanent=False)),

    url(r'^search/$', "search", name="accounts-search"),
    url(r'^orders/$', "orders", name="accounts-list_orders"),
    url(r'^settings/$', 'settings', name="accounts-settings"),
    url(r'^stats/$', 'stats', name="accounts-stats"),
    url(r'^updates/$', 'updates', name="accounts-updates"),

    url(r'^calendars/$', "calendars", name="calendars-list"),
    url(r'^calendars/new/$', "edit_calendar", name="calendars-create"),
    url(r'^calendars/(?P<pk>\d+)/$', "view_calendar", {'view': 'week'},
        name='calendars.view'),

    url(r'^calendars/(?P<pk>\d+)/delete/$', "delete_calendar",
        name='calendars-delete'),

    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/$', "view_calendar",
        name='calendars.view'),
    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/(?P<start_date>[0-9\-]+)/$', "view_calendar",
        name='calendars-view_calendar'),
    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/download/$', "download_calendar",
        name='calendars-download'),
    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/(?P<start_date>[0-9\-]+)/print/$', "print_calendar",
        name="calendars-print"),
    url(r'^calendars/(?P<pk>\d+)/(?P<view>[a-z]+)/edit/$', "edit_calendar",
        name='calendars-edit'),

    url(r'^calendars/(?P<cal_pk>\d+)/events/new/$', "edit_calendar_event",
        name='calendars.event.edit'),
    url(r'^calendars/(?P<cal_pk>\d+)/events/(?P<pk>\d+)/edit/$', "edit_calendar_event",
        name='calendars.event.edit'),
    url(r'^calendars/(?P<cal_pk>\d+)/events/(?P<pk>\d+)/delete/$', "delete_calendar_event",
        name='calendars.event.delete'),
    url(r'^calendars/(?P<cal_pk>\d+)/events/(?P<pk>\d+)/finish/$', "finish_calendar_event",
        name='calendars.event.finish'),

    url(r'^notifications/clear/$', "clear_notifications", name="accounts-clear_notifications"),

)
