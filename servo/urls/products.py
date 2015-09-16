# -*- coding: utf-8 -*-

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
