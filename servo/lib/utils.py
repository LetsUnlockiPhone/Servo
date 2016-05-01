# -*- coding: utf-8 -*-

import json
import html2text
import subprocess
from django.http import HttpResponse
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def file_type(buf):
    import magic
    return magic.from_buffer(buf, mime=True)


def paginate(queryset, page, count=10):
    """
    Shortcut for paginating a queryset
    """
    paginator = Paginator(queryset, count)

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    return results


def text_response(data):
    return HttpResponse(data, content_type='text/plain; charset=utf-8')


def csv_response(data):
    """
    Shortcut for sending a CSV response
    """
    return HttpResponse(data, content_type='text/csv')


def send_csv(data, filename):
    """
    Shortcut for sending CSV data as a file
    """
    response = text_response(data)
    response['Content-Disposition'] = 'attachment; filename="%s.txt"' % filename
    return response


def json_response(data):
    """
    Shortcut for sending a JSON response
    """
    return HttpResponse(json.dumps(data), content_type='application/json')


def strip_keypass(keypass, infile, outfile):
    """
    Strips a passphrase from a private key
    """
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


def unescape(s):
    import HTMLParser
    html_parser = HTMLParser.HTMLParser()
    return html_parser.unescape(s)


def html_to_text(s, ignore_images=False):
    h = html2text.HTML2Text()
    h.ignore_images = ignore_images
    return h.handle(s)


def gsx_to_text(s):
    return html_to_text(unescape(s))
