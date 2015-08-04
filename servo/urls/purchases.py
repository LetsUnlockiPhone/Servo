from django.conf.urls import patterns, url
from servo.views.product import choose_product

urlpatterns = patterns(
    "servo.views.purchases",
    url(r'^$', 'list_pos', name="purchases-list_pos"),

    url(r'^product/(?P<product_id>\d+)/order/$', 'create_po', name='purchases-create_po'),
    url(r'^po/create/$', 'create_po', {'order_id': None, 'product_id': None},
        name='purchases-create_po'),
    url(r'^po/(\d+)/edit/$', 'edit_po', name="purchases-edit_po"),
    url(r'^po/(\d+)/view/$', 'view_po', name="purchases-view_po"),
    url(r'^po/(\d+)/delete/$', 'delete_po', name="purchases-delete_po"),
    url(r'^po/(\d+)/order_stock/$', 'order_stock', name="purchases-submit_stock_order"),
    url(r'^po/(\d+)/purchases/choose/$', choose_product,
        {'target_url': "purchases-add_to_po"},
        name="purchases-choose_for_po"),
    url(r'^po/order/(?P<order_id>\d+)/$', 'create_po', name="purchases-create_po"),
    url(r'^po/(?P<pk>\d+)/purchases/(?P<product_id>\d+)/add/$', 'add_to_po',
        name="purchases-add_to_po"),
    url(r'^po/(?P<pk>\d+)/purchases/(?P<item_id>\d+)/delete/$', 'delete_from_po',
        name="purchases-delete_from_po"),

    url(r'^(\w+)/(\w+)/$', 'list_pos', name="purchases-browse_pos"),
)
