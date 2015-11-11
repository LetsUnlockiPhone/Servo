# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include

urlpatterns = patterns(
    "",
    url(r'^products/', include('servo.urls.products')),
    url(r'^purchases/', include('servo.urls.purchases')),
    url(r'^shipments/', include('servo.urls.shipments')),
    url(r'^invoices/', include('servo.urls.invoices')),
)
