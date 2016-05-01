# -*- coding: utf-8 -*-

from django.conf.urls import url

from servo.views.note import *


urlpatterns = [
    url(r'^$', list_notes, name="notes-list_notes"),
    url(r'^find/$', find, name="notes-find"),

    url(r'^templates/$', templates, name="notes-templates"),
    url(r'^new/$', edit, name="notes-create"),
    url(r'^templates/(\d+)/$', templates, name='notes-template'),
    url(r'^render/$', render_template, name='notes-render_template'),
    url(r'^render/(?P<order_id>\d+)/$', render_template,
        name='notes-render_template'),
    url(r'^to/customer/(?P<customer>\d+)/new/$', edit,
        name="notes-create_to_customer"),
    url(r'^(?P<pk>\d+)/toggle/tag/(?P<tag_id>\d+)/$', toggle_tag,
        name="notes-toggle_tag"),
    url(r'^(?P<kind>\w+)?/(?P<pk>\d+)/toggle_(?P<flag>[a-z]+)/$', toggle_flag,
        name="notes-toggle_flag"),
    url(r'^(?P<parent>\d+)/reply/$', edit, name="notes-reply"),
    url(r'^(?P<pk>\d+)/edit/$', edit, name="notes-edit"),
    url(r'^(?P<pk>\d+)/messages/$', list_messages, name="notes-messages"),
    url(r'^(?P<pk>\d+)/delete/$', delete_note, name='notes-delete_note'),
    url(r'^(?P<pk>\d+)/copy/$', copy, name='notes-copy'),
    url(r'^to/(?P<recipient>.+)/new/$', edit, name="notes-create_with_recipient"),
    url(r'^to/(?P<recipient>.+)/order/(?P<order_id>\d+)/$', edit,
        name="notes-create_with_to_and_order"),

    url(r'^escalations/new/$', create_escalation, name="notes-create_escalation"),

    url(r'^(?P<kind>\w+)/$', list_notes, name="notes-list_notes"),
    url(r'^(?P<kind>\w+)/(?P<pk>\d+)/view/$', view_note, name="notes-view_note"),
]
