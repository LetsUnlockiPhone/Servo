from django.conf.urls import patterns, url, include

from servo.views import api


urlpatterns = patterns(
    "servo.views.api",
    url(r'^status/$', api.OrderStatusView.as_view(), name='api-status'),
    url(r'^tags/$', 'tags', name='api-tags'),
    url(r'^users/$', 'users', name='api-users'),
    url(r'^queues/$', 'queues', name='api-queues'),
    url(r'^places/$', 'places', name='api-places'),
    url(r'^locations/$', 'locations', name='api-locations'),
    url(r'^statuses/$', 'statuses', name='api-statuses'),

    url(r'^orders/$', 'orders', name='api-order_create'),
    url(r'^orders/(\d{8})/$', 'orders', name='api-order_list'),
    url(r'^orders/(?P<pk>\d+)/$', 'orders', name='api-order_detail'),

    url(r'^warranty/$', 'warranty', name='api-device_warranty'),
    url(r'^messages/$', 'messages', name='api-messages'),
    url(r'^device_models/$', 'device_models'),

    url(r'^status/(?P<pk>\d+)/$', 'order_status', name='queuestatus-detail'),
    url(r'^notes/(?P<pk>\d+)/$', 'notes', name='api-note_detail'),
    url(r'^orders/products/(?P<pk>\d+)/$', 'order_items', name='api-order_items'),

    url(r'^users/(?P<pk>\d+)/$', 'user_detail', name='api-user_detail'),

    url(r'^customers/$', 'customers', name='api-customers'),
    url(r'^customers/(?P<pk>\d+)/$', 'customers', name='api-customer_detail'),

    url(r'^devices/(?P<pk>\d+)/$', 'devices', name='api-device_detail'),
)
