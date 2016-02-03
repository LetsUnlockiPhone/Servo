# -*- coding: utf-8 -*-

from django.conf.urls import url

from servo.views.gsx import *


urlpatterns = [
    url(r'^(\d+)/delete/$', delete_repair, name="repairs-delete_repair"),
    url(r'^(\d+)/parts/(\d+)/remove/$', remove_part, name="repairs-remove_part"),
    url(r'^(\d+)/parts/(\d+)/add/$', add_part, name="repairs-add_part"),
    url(r'^(\d+)/parts/(\d+)/update_sn/$', update_sn, name="repairs-update_sn"),
    url(r'^(\d+)/copy/$', copy_repair, name="repairs-copy_repair"),
    url(r'^(\d+)/check_parts/$', check_parts_warranty, name="repairs-check_parts"),
]
