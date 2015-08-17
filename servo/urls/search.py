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
