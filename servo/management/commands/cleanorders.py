# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from servo.models import Order


class Command(BaseCommand):

    help = "Deletes empty service orders"

    def handle(self, *args, **options):
        orders = Order.objects.filter(customer=None,
                                      devices=None,
                                      note=None,
                                      serviceorderitem=None)
        count = orders.count()
        orders.delete()
        print('%d orders deleted' % count)
