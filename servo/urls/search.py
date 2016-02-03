# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.decorators.cache import cache_page

from servo.views.search import search_gsx, get_gsx_search_results

from servo.views.search import *

urlpatterns = [
    url(r'^$', spotlight, name="search-spotlight"),
    url(r'^customers/$', customers, name="search-customers"),
    url(r'^devices/(?P<what>\w+)/(?P<param>\w+)/(?P<query>[~\w\s,\-\(\)/\.]+)/$',
        search_gsx,
        name="search-search_gsx"),
    url(r'^gsx/(?P<what>\w+)/(?P<param>\w+)/(?P<query>[~\w\s,\-\(\)/\.]+)/$',
        #cache_page(60*15)(get_gsx_search_results),
        get_gsx_search_results,
        name="search-get_gsx_search_results"),
]
