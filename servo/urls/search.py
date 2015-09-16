# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from servo.views.search import search_gsx

urlpatterns = patterns(
    "servo.views.search",
    url(r'^$', "spotlight",
        name="search-spotlight"),
    url(r'^gsx/(?P<what>\w+)/$', "list_gsx",
        name="search-gsx"),
    url(r'^gsx/(?P<what>\w+)/for/(?P<q>\w+)/$', "list_gsx",
        name="search-gsx"),
    # /search/gsx/parts/?productName=iPod+Shuffle...
    url(r'^gsx/(?P<what>\w+)/(?P<arg>\w+)/(?P<value>[~\w\s,\-\(\)/\.]+)/$',
        cache_page(60*15)(search_gsx),
        name="search-search_gsx"),
    url(r'^gsx/(?P<what>\w+)/results/$', "view_gsx_results",
        name="search-gsx_results"),
    url(r'^notes/$', "list_notes"),
    url(r'^products/$', "list_products"),
    url(r'^orders/$', "list_orders"),
    url(r'^customers/$', "list_customers"),
    url(r'^devices/$', "list_devices"),
    url(r'^gsx/$', "list_gsx"),
    url(r'^articles/$', "list_articles"),
)
