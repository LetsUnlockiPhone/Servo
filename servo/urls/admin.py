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
from servo.views import admin


urlpatterns = patterns(
    'servo.views.admin',
    url(r'^settings/$', 'settings', name='admin-settings'),

    url(r'^statuses/$', 'statuses', name='admin-statuses'),
    url(r'^statuses/new/$', 'edit_status', name="admin-create_status"),
    url(r'^statuses/(\d+)/edit/$', 'edit_status', name="admin-edit_status"),
    url(r'^statuses/(\d+)/delete/$', 'remove_status', name="admin-delete_status"),

    url(r'^users/$', 'list_users', name='admin-list_users'),
    url(r'^users/new/$', 'edit_user', name="admin-create_user"),
    url(r'^users/upload/$', 'upload_users', name="admin-upload_users"),
    url(r'^users/(\d+)/edit/$', 'edit_user', name="admin-edit_user"),
    url(r'^users/(\d+)/delete/$', 'delete_user', name="admin-delete_user"),
    url(r'^users/(\d+)/delete_tokens/$', 'delete_user_token', name="admin-delete_user_token"),
    url(r'^users/(\d+)/create_token/$', 'create_user_token', name="admin-create_user_token"),

    url(r'^groups/$', 'list_groups', name='admin-list_groups'),
    url(r'^groups/new/$', 'edit_group', name="admin-create_group"),
    url(r'^groups/(\d+)/edit/$', 'edit_group', name="admin-edit_group"),
    url(r'^groups/(\d+)/delete/$', 'delete_group', name="admin-delete_group"),

    url(r'^tags/$', 'tags', name='admin-tags'),
    url(r'^tags/(?P<type>[a-z]+)/$', 'tags', name='admin-tags'),
    url(r'^tags/(?P<type>[a-z]+)/new/$', 'edit_tag', name="admin-create_tag"),
    url(r'^tags/[a-z]+/(?P<pk>\d+)/delete/$', 'delete_tag', name="admin-delete_tag"),
    url(r'^tags/(?P<type>[a-z]+)/(?P<pk>\d+)/$', 'edit_tag', name="admin-edit_tag"),

    url(r'^fields/(?P<type>[a-z]+)/$', 'fields', name='admin-fields'),
    url(r'^fields/(?P<type>[a-z]+)/new/$', 'edit_field', name="admin-create_field"),
    url(r'^fields/[a-z]+/(\d+)/delete/$', 'delete_field', name="admin-delete_field"),
    url(r'^fields/(?P<type>[a-z]+)/(?P<pk>\d+)/edit/$', 'edit_field', name="admin-edit_field"),

    url(r'^templates/$', 'list_templates', name='admin-list_templates'),
    url(r'^templates/new/$', 'edit_template', name='admin-edit_template'),
    url(r'^templates/(\d+)/edit/$', 'edit_template', name='admin-edit_template'),
    url(r'^templates/(\d+)/delete/$', 'delete_template', name='admin-delete_template'),

    url(r'^queues/$', 'queues', name='admin-queues'),
    #url(r'^queues/$', admin.QueueListView.as_view(), name='admin-queues'),
    url(r'^queues/new/$', 'edit_queue', name="admin-create_queue"),
    url(r'^queues/(?P<pk>\d+)/edit/$', 'edit_queue', name="admin-edit_queue"),
    #url(r'^queues/(?P<pk>\d+)/edit/$', admin.QueueListView.as_view(), name='admin-edit_queue'),
    url(r'^queues/(\d+)/delete/$', 'delete_queue', name="admin-delete_queue"),

    url(r'^gsx/accounts/$', 'list_gsx_accounts', name='admin-list_gsx_accounts'),
    url(r'^gsx/accounts/new/$', 'edit_gsx_account', name='admin-edit_gsx_account'),
    url(r'^gsx/accounts/(\d+)/$', 'edit_gsx_account', name='admin-edit_gsx_account'),
    url(r'^gsx/accounts/(\d+)?/delete/$', 'delete_gsx_account', name='admin-delete_gsx_account'),

    url(r'^locations/$', 'locations', name='admin-locations'),
    url(r'^locations/new/$', 'edit_location', name='admin-create_location'),
    url(r'^locations/(\d+)/edit/$', 'edit_location', name='admin-edit_location'),
    url(r'^locations/(\d+)/delete/$', 'delete_location', name='admin-delete_location'),

    url(r'^notifications/$', 'notifications', name='admin-notifications'),
    url(r'^notifications/(\w+)/$', 'edit_notification'),

    url(r'^checklists/$', 'checklists', name='admin-checklists'),
    url(r'^checklists/new/$', 'edit_checklist', name='admin-create_checklist'),
    url(r'^checklists/(?P<pk>\d+)/edit/$', 'edit_checklist', name='admin-edit_checklist'),
    url(r'^checklists/(?P<pk>\d+)/delete/$', 'delete_checklist', name='admin-delete_checklist'),

    url(r'^sites/$', 'list_sites', name="admin-list_sites"),
    url(r'^sites/new/$', 'edit_site', name="admin-create_site"),
    url(r'^sites/(\d+)/edit/$', 'edit_site', name="admin-edit_site"),

    url(r'^rules/', include('servo.urls.rules')),

    url(r'^backups/$', 'backups', name="admin-backups"),

)
