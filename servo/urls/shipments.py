# -*- coding: utf-8 -*-

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
