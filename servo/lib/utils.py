# -*- coding: utf-8 -*-

import json
from django.db.models import Model
from django.core.serializers.json import DjangoJSONEncoder


def strip_keypass(keypass, infile, outfile):
    """
    Strips a passphrase from a private key
    """
    import subprocess
    subprocess.call(['openssl', 'rsa', '-passin', 'pass:' + keypass,
                     '-in', infile, '-out', outfile])

def multiprint(*args):
    """
    Emulate JS console.log()
    """
    print(', '.join(args))

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

    val = v()
    cache.set(k, val)
    return val


class SessionSerializer:
    def dumps(self, obj):
        return json.dumps(obj, cls=DjangoJSONEncoder)

    def loads(self, data):
        return json.loads(data, cls=DjangoJSONEncoder)
