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
    "servo.views.customer",
    url(r'^$', 'index', {'group': 'all'}, name="customers-list_all"),
    url(r'^find/$', 'find', name="customers-find"),
    url(r'^search/$', 'search', name="customers-search"),
    url(r'^filter/$', 'filter', name="customers-filter"),
    url(r'^download/$', 'download', name="customers-download"),
    url(r'^download/(?P<group>[\w\-]+)/$', 'download', name="customers-download"),
    url(r'^find/download$', 'download', name="customers-download_search"),
    url(r'^groups/add/$', 'edit_group', name="customers-create_group"),
    url(r'^groups/(?P<group>[\w\-]+)/edit/$', 'edit_group', name="customers-edit_group"),
    url(r'^groups/(?P<group>[\w\-]+)/delete/$', 'delete_group', name="customers-delete_group"),
    url(r'^(?P<group>[\w\-]+)/$', 'index', name="customers-list"),
    url(r'^(?P<group>[\w\-]+)/upload/$', 'upload', name="customers-upload"),
    url(r'^(?P<group>[\w\-]+)/add/$', 'edit', name="customers-create_customer"),
    url(r'^(?P<group>[\w\-]+)/(?P<pk>\d+)/$', 'view', name="customers-view_customer"),
    url(r'^(?P<group>[\w\-]+)/(?P<pk>\d+)/edit/$', 'edit', name="customers-edit_customer"),
    url(r'^(?P<group>[\w\-]+)/(?P<pk>\d+)/delete/$', 'delete', name="customers-delete_customer"),
    url(r'^(?P<pk>\d+)/move/$', 'move', name="customers-move_customer"),
    url(r'^(?P<pk>\d+)/move/(?P<new_parent>\d+)/$', 'move', name="customers-move_customer"),
    url(r'^(?P<pk>\d+)/merge/$', 'merge', name="customers-merge_customer"),
    url(r'^(?P<pk>\d+)/merge/(?P<target>\d+)/$', 'merge', name="customers-merge_customer"),
    url(r'^(?P<parent_id>\d+)/new/$', 'edit', name="customers-create_contact"),
    url(r'^(\d+)/orders/(\d+)/$', 'add_order', name="customers-add_to_order"),
    url(r'^(?P<pk>\d+)/notes/$', 'notes', name="customers-list_notes"),
    url(r'^(?P<pk>\d+)/notes/new/$', 'create_message', name="customers-create_message"),
)
