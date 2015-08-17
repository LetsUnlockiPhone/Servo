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

from django.conf.urls import patterns, url, include
from servo.views import api

urlpatterns = patterns(
    "servo.views.api",
    url(r'^status/$', api.OrderStatusView.as_view(), name='api-status'),
    url(r'^tags/$', 'tags', name='api-tags'),
    url(r'^users/$', 'users', name='api-users'),
    url(r'^queues/$', 'queues', name='api-queues'),
    url(r'^places/$', 'places', name='api-places'),
    url(r'^locations/$', 'locations', name='api-locations'),
    url(r'^statuses/$', 'statuses', name='api-statuses'),

    url(r'^orders/$', 'orders', name='api-order_create'),
    url(r'^orders/(\d{8})/$', 'orders', name='api-order_list'),
    url(r'^orders/(?P<pk>\d+)/$', 'orders', name='api-order_detail'),

    url(r'^warranty/$', 'warranty', name='api-device_warranty'),
    url(r'^messages/$', 'messages', name='api-messages'),
    url(r'^device_models/$', 'device_models'),

    url(r'^status/(?P<pk>\d+)/$', 'order_status', name='queuestatus-detail'),
    url(r'^notes/(?P<pk>\d+)/$', 'notes', name='api-note_detail'),
    url(r'^orders/products/(?P<pk>\d+)/$', 'order_items', name='api-order_items'),

    url(r'^users/(?P<pk>\d+)/$', 'user_detail', name='api-user_detail'),

    url(r'^customers/$', 'customers', name='api-customers'),
    url(r'^customers/(?P<pk>\d+)/$', 'customers', name='api-customer_detail'),

    url(r'^devices/(?P<pk>\d+)/$', 'devices', name='api-device_detail'),
)
