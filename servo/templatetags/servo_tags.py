# -*- coding: utf-8 -*-

import re
import decimal

from gsxws import objectify

import babel.numbers
from datetime import timedelta

from django import template
from django.utils import safestring, timezone
from django.utils.translation import ugettext as _
from django.template.defaultfilters import date
from django.contrib.humanize.templatetags.humanize import naturaltime

from servo.models.common import Configuration

register = template.Library()


@register.filter
def gsx_diags_ts(value):
    return objectify.gsx_diags_timestamp(value)


@register.filter
def unread_notifications(queryset):
    queryset = queryset.filter(action='set_status', handled_at=None)
    return queryset.order_by('-handled_at')


@register.filter
def unread_messages(queryset):
    queryset = queryset.filter(action='note_added', handled_at=None)
    return queryset.order_by('-handled_at')


@register.filter
def count_or_empty(queryset):
    if queryset.count() > 0:
        return queryset.count()
    return ''


@register.filter
def search_url(request):
    "Returns the proper search URL"
    prefix = request.path.split("/")[1]
    return "/%s/search/" % prefix


@register.filter
def str_find(string, substr):
    return (string.find(substr) > -1)


@register.filter(expects_localtime=True, is_safe=False)
def relative_date(value):
    if value in ('', None):
        return ''

    current = timezone.now()
    
    if (current - value) > timedelta(days=1):
        return date(value, "SHORT_DATETIME_FORMAT")
        
    return naturaltime(value)


@register.filter(is_safe=True)
def highlight(text, string):
    result = re.sub(r'('+string+')', '<span class="highlight">\g<0></span>', text)
    return result


@register.filter
def amount_in_location(obj, user):
    """
    Returns how many instances of this product
    are at the current user's location
    """
    return obj.get_amount_stocked(user)


@register.filter
def is_item_complete(obj, item):
    return obj.is_item_complete(item)


@register.filter
def item_completed_by(obj, item):
    item = is_item_complete(obj, item)

    try:
        return item.checked_by.username
    except Exception:
        return ''


@register.filter
def widget_is(obj, widget):
    try:
        return obj.field.widget.__class__.__name__ == widget
    except AttributeError:
        return False


@register.filter(is_safe=True)
def currency(value):
    try:
        c = Configuration.conf('currency')
        return babel.numbers.format_currency(decimal.Decimal(value), c)
    except Exception:
        return value


@register.simple_tag
def active(request, *args):
    s = '/'.join([str(i) for i in args])
    pattern = s[:-1] if s.endswith('//') else s
    path = request.path.lstrip('/')
    return 'active' if re.search(pattern, path) else ''


@register.simple_tag
def active_url(request, url):
    return 'active' if request.path == url else ''


@register.simple_tag
def paginator_page(request, page):
    query = request.GET.copy()
    if 'page' in query.keys():
        del query['page']
    query['page'] = page
    return query.urlencode()


@register.filter
def markdown(text):
    import markdown
    result = markdown.markdown(text)
    return safestring.mark_safe(result)


@register.filter
def concat(str1, str2):
    return str(str1) + str(str2)


@register.filter
def addspace(s):
    return str(s).replace(',', ', ')


@register.filter
def device_accessories(device, order):
    return device.get_accessories(order)


@register.filter
def replace(value, arg):
    old, new = arg.split(",")
    return value.replace(old, new)
