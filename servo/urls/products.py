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
    "servo.views.product",

    url(r'^tags/$', "tags", name="products-tags"),
    url(r'^all/$', "list_products", {'group': 'all'}, name="products-list_products"),
    url(r'^download/$', "download_products", name="products-download"),
    url(r'^upload/$', "upload_products", name="products-upload_products"),
    url(r'^upload/parts/$', "upload_gsx_parts", name="products-upload_gsx_parts"),
    url(r'^update_price/(\d+)/$', "update_price", name="products-update_price"),

    url(r'^all/(?P<pk>\d+)/$', "view_product", {'group': 'all'}, name="products-view_product"),
    url(r'^(?P<group>[\w\-/]*)/(?P<pk>\d+)/view/$', "view_product",
        name="products-view_product"),

    # Editing product categories
    url(r'^categories/create/$', "edit_category", name="products-create_category"),
    url(r'^categories/(?P<slug>[\w\-]+)/edit/$',
        "edit_category",
        name="products-edit_category"),
    url(r'^categories/(?P<slug>[\w\-]+)/delete/$',
        "delete_category",
        name="products-delete_category"),
    url(r'^categories/(?P<parent_slug>[\w\-]+)/create/$',
        "edit_category",
        name="products-create_category"),

    # Editing products
    url(r'^create/$', "edit_product", name="products-create"),
    url(r'^(?P<group>[\w\-]+)/create/$', "edit_product", name="products-create"),
    url(r'^(?P<group>[\w\-/]*)/(?P<pk>\d+)/edit/$', "edit_product",
        name="products-edit_product"),
    url(r'^(?P<group>[\w\-/]*)/(?P<pk>\d+)/delete/$', "delete_product",
        name="products-delete_product"),

    # Choosing a product for an order
    url(r'^choose/order/(?P<order_id>\d+)/$', "choose_product", name="products-choose"),

    url(r'^(?P<group>[\w\-]+)/(?P<code>[\w\-/]+)/create/$', "edit_product",
        name="products-create"),
    url(r'^all/(?P<code>[\w\-/]+)/view/$',
        "view_product", {'group': 'all'},
        name="products-view_product"),
    url(r'^(?P<code>[\w\-/]+)/new/$',
        "edit_product", {'group': None},
        name="products-create"),

    url(r'^code/(?P<code>[\w\-/]+)/location/(?P<location>\d+)/get_info/$',
        "get_info",
        name="products-get_info"),

    url(r'^(?P<group>[\w\-]+)/$', "list_products", name="products-list_products"),
)
