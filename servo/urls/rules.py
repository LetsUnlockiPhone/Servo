# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'servo.views.rules',
    url(r'^$', 'list_rules', name='rules-list_rules'),
    url(r'^add/$', 'edit_rule', name='rules-create'),
    url(r'^(?P<pk>\d+)$', 'view_rule', name='rules-view_rule'),
    url(r'^(?P<pk>\d+)/edit/$', 'edit_rule', name='rules-edit_rule'),
    url(r'^(?P<pk>\d+)/delete/$', 'delete_rule', name='rules-delete_rule'),
)
