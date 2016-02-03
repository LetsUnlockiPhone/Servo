# -*- coding: utf-8 -*-

from django.conf.urls import url

from servo.views.invoices import *


urlpatterns = [
    url(r'^$', invoices, name="invoices-index"),
    url(r'^gsx/$', gsx_invoices, name="invoices-gsx_invoices"),

    url(r'^(?P<pk>\d+)/$', view_invoice, name="invoices-view_invoice"),
    url(r'^(?P<pk>\d+)/print/$', print_invoice, name="invoices-print_invoice"),
]
