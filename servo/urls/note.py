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
    "servo.views.note",
    url(r'^$', 'list_notes', name="notes-list_notes"),
    url(r'^search/$', 'search', name="notes-search"),
    url(r'^find/$', 'find', name="notes-find"),

    url(r'^templates/$', 'templates'),
    url(r'^new/$', 'edit', name="notes-create"),
    url(r'^templates/(\d+)/$', 'templates', name='notes-template'),
    url(r'^render_template/$', 'render_template', name='notes-render_template'),
    url(r'^to/customer/(?P<customer>\d+)/new/$', 'edit', name="notes-create_to_customer"),
    url(r'^(?P<pk>\d+)/toggle/tag/(?P<tag_id>\d+)/$', 'toggle_tag', name="notes-toggle_tag"),
    url(r'^(?P<pk>\d+)/toggle/(?P<flag>[a-z]+)/$', 'toggle_flag', name="notes-toggle_flag"),
    url(r'^(?P<parent>\d+)/reply/$', 'edit', name="notes-reply"),
    url(r'^(?P<pk>\d+)/edit/$', 'edit', name="notes-edit"),
    url(r'^(?P<pk>\d+)/messages/$', 'list_messages', name="notes-messages"),
    url(r'^(?P<pk>\d+)/delete/$', 'delete_note', name='notes-delete_note'),
    url(r'^(?P<pk>\d+)/copy/$', 'copy', name='notes-copy'),
    url(r'^to/(?P<recipient>.+)/new/$', 'edit', name="notes-create_with_recipient"),
    url(r'^to/(?P<recipient>.+)/order/(?P<order_id>\d+)/$', 'edit',
        name="notes-create_with_to_and_order"),

    url(r'^escalations/new/$', 'create_escalation', name="notes-create_escalation"),

    url(r'^(?P<kind>\w+)/$', 'list_notes', name="notes-list_notes"),
    url(r'^(?P<kind>\w+)/(?P<pk>\d+)/view/$', 'view_note', name="notes-view_note"),
)
