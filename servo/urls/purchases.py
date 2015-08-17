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
from servo.views.product import choose_product

urlpatterns = patterns(
    "servo.views.purchases",
    url(r'^$', 'list_pos', name="purchases-list_pos"),

    url(r'^product/(?P<product_id>\d+)/order/$', 'create_po', name='purchases-create_po'),
    url(r'^po/create/$', 'create_po', {'order_id': None, 'product_id': None},
        name='purchases-create_po'),
    url(r'^po/(\d+)/edit/$', 'edit_po', name="purchases-edit_po"),
    url(r'^po/(\d+)/view/$', 'view_po', name="purchases-view_po"),
    url(r'^po/(\d+)/delete/$', 'delete_po', name="purchases-delete_po"),
    url(r'^po/(\d+)/order_stock/$', 'order_stock', name="purchases-submit_stock_order"),
    url(r'^po/(\d+)/purchases/choose/$', choose_product,
        {'target_url': "purchases-add_to_po"},
        name="purchases-choose_for_po"),
    url(r'^po/order/(?P<order_id>\d+)/$', 'create_po', name="purchases-create_po"),
    url(r'^po/(?P<pk>\d+)/purchases/(?P<product_id>\d+)/add/$', 'add_to_po',
        name="purchases-add_to_po"),
    url(r'^po/(?P<pk>\d+)/purchases/(?P<item_id>\d+)/delete/$', 'delete_from_po',
        name="purchases-delete_from_po"),

    url(r'^(\w+)/(\w+)/$', 'list_pos', name="purchases-browse_pos"),
)
