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
from django.views.decorators.cache import cache_page

from servo.views.order import create
from servo.views.device import get_gsx_search_results

urlpatterns = patterns(
    "servo.views.device",
    url(r'^$', 'index', name="devices-list"),

    url(r'^search/$', 'search'),
    url(r'^find/$', "find", name="devices-find"),
    url(r'^add/$', "edit_device", name="devices-add"),

    url(r'^(?P<pk>\d+)/diags/$', 'diagnostics', name="devices-diagnostics"),

    url(r'^(?P<pk>\d+)/update_gsx_details/$', "update_gsx_details", name="devices-update_gsx_details"),
    url(r'^(?P<pk>\d+)/orders/(?P<order_id>\d+)/queue/(?P<queue_id>\d+)/parts/$',
        "parts", name="devices-parts"),

    url(r'^search/gsx/(?P<what>\w+)/(?P<param>\w+)/(?P<query>[~\w\s,\-\(\)/\.]+)/$',
        "search_gsx",
        name="devices-search_gsx"),

    url(r'^search/gsx/(?P<what>\w+)/(?P<param>\w+)/(?P<query>[~\w\s,\-\(\)/\.]+)/$',
        cache_page(60*15)(get_gsx_search_results),
        name="devices-get_gsx_search_results"),

    url(r'^choose/order/(\d+)/$', 'choose', name="devices-choose"),
    url(r'^upload/$', 'upload_devices', name="devices-upload_devices"),
    url(r'^(?P<device_id>\d+)/orders/create/$', create, name="devices-create_order"),
    url(r'^(?P<pk>\d+)/get_info/$', 'get_info', name="devices-get_info"),

    url(r'^(?P<product_line>\w+)/$', "index", name="devices-list_devices"),
    url(r'^(?P<product_line>\w+)/(?P<model>[\w\-]+)/$', "index",
        name="devices-list_devices"),
    url(r'^(?P<product_line>\w+)/(?P<model>[\w\-]+)/parts/$', "model_parts",
        name="devices-model_parts"),
    url(r'^(?P<product_line>\w+)/(?P<model>[\w\-]+)/(?P<pk>\d+)/$', "view_device",
        name="devices-view_device"),

    url(r'^(?P<product_line>\w+)/(?P<model>[\w-]+)/(?P<pk>\d+)/edit/$', "edit_device",
        name="devices-edit_device"),
    url(r'^(?P<product_line>\w+)/(?P<model>[\w-]+)/create/$', "edit_device",
        name="devices-create_device"),
    url(r'^(?P<product_line>\w+)/(?P<model>[\w-]+)/(?P<pk>\d+)/delete/$', "delete_device",
        name="devices-delete_device"),

    url(r'^search$', 'search', name="devices-search"),
)
