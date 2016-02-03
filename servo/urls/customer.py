# -*- coding: utf-8 -*-

from django.conf.urls import url

from servo.views.customer import *


urlpatterns = [
    url(r'^$', index, {'group': 'all'}, name="customers-list_all"),
    url(r'^find/$', find, name="customers-find"),
    url(r'^filter/$', filter, name="customers-filter"),
    url(r'^download/$', download, name="customers-download"),
    url(r'^download/(?P<group>[\w\-]+)/$', download, name="customers-download"),
    url(r'^find/download$', download, name="customers-download_search"),
    url(r'^groups/add/$', edit_group, name="customers-create_group"),
    url(r'^groups/(?P<group>[\w\-]+)/edit/$', edit_group,
        name="customers-edit_group"),
    url(r'^groups/(?P<group>[\w\-]+)/delete/$', delete_group,
        name="customers-delete_group"),
    url(r'^(?P<group>[\w\-]+)/$', index, name="customers-list"),
    url(r'^(?P<group>[\w\-]+)/upload/$', upload, name="customers-upload"),
    url(r'^(?P<group>[\w\-]+)/add/$', edit, name="customers-create_customer"),
    url(r'^(?P<group>[\w\-]+)/(?P<pk>\d+)/$', view,
        name="customers-view_customer"),
    url(r'^(?P<group>[\w\-]+)/(?P<pk>\d+)/edit/$', edit,
        name="customers-edit_customer"),
    url(r'^(?P<group>[\w\-]+)/(?P<pk>\d+)/delete/$', delete,
        name="customers-delete_customer"),
    url(r'^(?P<pk>\d+)/move/$', move, name="customers-move_customer"),
    url(r'^(?P<pk>\d+)/move/(?P<new_parent>\d+)/$', move,
        name="customers-move_customer"),
    url(r'^(?P<pk>\d+)/merge/$', merge, name="customers-merge_customer"),
    url(r'^(?P<pk>\d+)/merge/(?P<target>\d+)/$', merge,
        name="customers-merge_customer"),
    url(r'^(?P<parent_id>\d+)/new/$', edit, name="customers-create_contact"),
    url(r'^(\d+)/orders/(\d+)/$', add_order, name="customers-add_to_order"),
    url(r'^(?P<pk>\d+)/notes/$', notes, name="customers-list_notes"),
    url(r'^(?P<pk>\d+)/notes/new/$', create_message, name="customers-create_message"),
]
