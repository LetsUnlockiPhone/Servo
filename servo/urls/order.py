# -*- coding: utf-8 -*-

from servo.views import note
from django.conf.urls import patterns, url
from servo.views.order import update_order
from servo.views.invoices import create_invoice
from servo.views.gsx import create_repair, edit_repair, import_repair


urlpatterns = patterns(
    "servo.views.order",

    url(r'^$', 'list_orders', name='orders-index'),
    url(r'^\?queue=(?P<queue>\d+)$', 'list_orders', name='orders-list_queue'),
    url(r'^batch/$', 'batch_process', name="orders-batch_process"),
    url(r'^download/$', 'download_results', name="orders-download_results"),

    # Update commands
    url(r'^(\d+)/set_([a-z]+)/(\d+)/$', update_order, name="orders-update"),
    url(r'^(\d+)/users/(\d+)/remove/$', "remove_user", name="orders-remove_user"),

    url(r'^new/$', 'create', name='orders-create'),
    url(r'^(\d+)/$', 'edit', name='orders-edit'),

    url(r'^(?P<pk>\d+)/$', 'edit', name='order-detail'),

    url(r'^(\d+)/delete/$', "delete", name="orders-delete_order"),
    url(r'^(\d+)/copy/$', "copy_order", name="orders-copy_order"),
    url(r'^(\d+)/follow/$', 'toggle_follow', name="orders-toggle_follow"),
    url(r'^(\d+)/unfollow/$', 'toggle_follow'),

    url(r'^(\d+)/flag/$', 'toggle_flagged', name="orders-toggle_flagged"),
    url(r'^(\d+)/events/$', 'events', name="orders-list_events"),
    url(r'^(\d+)/repairs/(\d+)/$', 'repair', name="repairs-view_repair"),
    url(r'^(\d+)/repairs/(\d+)/close/$', 'complete_repair', 
        name="repairs-complete_repair"),
    url(r'^(\d+)/device/(\d+)/queue/(\d+)/parts/$', 'parts', 
        name="orders-list_parts"),
    url(r'^(\d+)/remove_device/(\d+)/$', "remove_device", 
        name='orders-delete_device'),

    url(r'^(?P<pk>\d+)/add_device/(?P<device_id>\d+)/$', "add_device", 
        name="orders-add_device"),
    url(r'^(?P<pk>\d+)/add_device/(?P<sn>\w+)/$', "add_device", 
        name="orders-add_device"),

    url(r'^(\d+)/products/$', 'products'),
    url(r'^(\d+)/list_products/$', 'list_products', name="orders-list_products"),

    url(r'^(\d+)/close/$', 'close', name='orders-close'),
    url(r'^(\d+)/reopen/$', 'reopen_order', name='orders-reopen_order'),
    url(r'^(\d+)/tags/(\d+)/toggle/$', 'toggle_tag', name='orders-toggle_tag'),
    url(r'^(\d+)/tasks/(\d+)/toggle/$', 'toggle_task', name='orders-toggle_task'),
    url(r'^(\d+)/dispatch/$', create_invoice, name='orders-dispatch'),
    url(r'^(\d+)/products/reserve/$', 'reserve_products', 
        name="orders-reserve_products"),
    url(r'^(\d+)/products/(\d+)/create_device/$', 'device_from_product',
        name="orders-create_device"),

    url(r'^(?P<pk>\d+)/customer/choose/', 'choose_customer', 
        name="orders-choose_customer"),
    url(r'^(?P<pk>\d+)/customer/(?P<customer_id>\d+)/select/$', 'select_customer',
        name="orders-select_customer"),
    url(r'^(?P<pk>\d+)/customer/(?P<customer_id>\d+)/remove/$', 'remove_customer',
        name="orders-remove_customer"),

    url(r'^create/product/(?P<product_id>\d+)/$', 'create', 
        name="orders-create_with_product"),
    url(r'^create/note/(?P<note_id>\d+)/$', 'create',
        name="orders-create_with_note"),
    url(r'^create/device/(?P<device_id>\d+)/$', 'create', 
        name='orders-create_with_device'),
    url(r'^create/sn/(?P<sn>\w+)?/$', 'create',
        name='orders-create_with_sn'),
    url(r'^create/customer/(?P<customer_id>\d+)?/$', 'create', 
        name="orders-create_with_customer"),

    url(r'^(?P<pk>\d+)/device/(?P<device_id>\d+)/accessories/$', 'accessories',
        name='orders-accessories'),
    url(r'^(?P<order_id>\d+)/device/(?P<device_id>\d+)/accessories/(?P<pk>\d+)/delete/$',
        'delete_accessory', name='orders-delete_accessory'),

    url(r'^(?P<pk>\d+)/print/(?P<kind>\w+)?/$', 'put_on_paper', 
        name="orders-print_order"),

    url(r'^(?P<pk>\d+)/products/(?P<item_id>\d+)/remove/$', 'remove_product',
        name='orders-remove_product'),
    url(r'^(?P<pk>\d+)/products/(?P<product_id>\d+)/add/$', 'add_product',
        name="orders-add_product"),
    url(r'^(?P<pk>\d+)/devices/(?P<device>\d+)/parts/(?P<code>[\w\-/]+)/add/$',
        'add_part', 
        name="orders-add_part"),
    url(r'^(?P<pk>\d+)/devices/(?P<device>\d+)/history/$', 'history', 
        name="orders-history"),
    url(r'^(?P<pk>\d+)/products/(?P<item_id>\d+)/report/$', 'report_product',
        name="orders-report_product"),
    url(r'^(?P<pk>\d+)/devices/(?P<device_id>\d+)/report/$', 'report_device',
        name="orders-report_device"),
    url(r'^(?P<pk>\d+)/products/(?P<item_id>\d+)/edit/$', 'edit_product',
        name="orders-edit_product"),
    url(r'^(?P<pk>\d+)/products/(?P<item_id>\d+)/(?P<action>\w+)/$', 'products'),

    url(r'^(?P<order_id>\d+)/notes/new/$', note.edit, name="orders-add_note"),
    url(r'^(?P<order_id>\d+)/notes/(?P<pk>\d+)/$', note.edit, 
        name="orders-edit_note"),
    url(r'^(\d+)/device/(\d+)/repairs/(\w+)/create/$', create_repair, 
        name="repairs-create_repair"),
    url(r'^(\d+)/device/(\d+)/import_repair/$', import_repair, 
        name="repairs-import_repair"),
    url(r'^(\d+)/repairs/(\d+)/edit/$', edit_repair, name="repairs-edit_repair"),

)
