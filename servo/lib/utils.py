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

def choices_to_dict(t):
    """
    Converts a ChoiceField two-tuple to a dict (for JSON)
    Assumes i[0][0] is always unique
    """
    d = {}
    for i in t:
        k = str(i[0])
        d[k] = i[1]

    return d

def empty(v):
    return v in ('', ' ', None,)

def cache_getset(k, v):
    """
    Shortcut for getting and setting cache
    v should be a callable
    """
    from django.core.cache import cache
    if cache.get(k):
        return cache.get(k)

    cache.set(k, v())
    return v
