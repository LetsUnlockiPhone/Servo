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

urlpatterns = patterns(
    "servo.views.shipments",
    url(r'^returns/list/$', "list_bulk_returns", name="shipments-list_bulk_returns"),
    url(r'^returns/pending/$', "edit_bulk_return", name="shipments-edit_bulk_return"),
    url(r'^returns/pending/(?P<ship_to>\d+)/$', "edit_bulk_return", name="shipments-edit_bulk_return"),
    url(r'^returns/(?P<pk>\d+)/$', "view_bulk_return", name="shipments-view_bulk_return"),
    url(r'^returns/(?P<pk>\d+)/packing_list/$', "view_packing_list", name="shipments-view_packing_list"),

    url(r'^incoming/$', "list_incoming", name="shipments-list_incoming"),
    url(r'^incoming/(?P<pk>\d+)/$', "view_incoming", name="shipments-view_incoming"),

    url(r'^returns/(?P<pk>\d+)/verify/$', "verify", name="shipments-verify"),

    url(r'^returns/$', 'list_returns', name="shipments-returns"),
    url(r'^incoming/date/$', 'list_incoming', {'status': 'received'}),
    url(r'^returns/(?P<pk>\d+)/parts/(?P<part_pk>\d+)/remove/$', 'remove_from_return',
        name="shipments-remove_from_return"),
    url(r'^returns/(?P<pk>\d+)/parts/add/$', 'add_to_return',
        name="shipments-pick_for_return"),
    url(r'^returns/(?P<pk>\d+)/parts/(?P<part>\d+)/$', 'add_to_return',
        name="shipments-add_to_return"),
    url(r'^(?P<code>[\w\-/]+)/return_label/(?P<return_order>\d+)/$', 'return_label',
        name="shipments-return_label"),
    url(r'^(?P<part>\d+)/update/return_type/(?P<return_type>\d{1})/', 'update_part',
        name="shipments-update_part"),
)
