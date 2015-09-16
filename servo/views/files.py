# -*- coding: utf-8 -*-

import os
import mimetypes
from django.conf import settings
from django.http import HttpResponse, Http404

from servo.models.common import Attachment


def view_file(request, pk):
    doc = Attachment.objects.get(pk=pk)
    return HttpResponse(doc.content.read(), content_type=doc.mime_type)


def get_file(request, path):
    """
    Returns a file from the upload directory
    """
    try:
        f = open(os.path.join(settings.MEDIA_ROOT, path), 'r')
    except IOError:
        raise Http404
    
    mimetypes.init()
    t, e = mimetypes.guess_type(f.name)

    return HttpResponse(f.read(), t)
