# -*- coding: utf-8 -*-

import sys
import logging

from django.core.management.base import BaseCommand
from servo.models import (Product, GsxAccount, User,)


class Command(BaseCommand):
    help = "Updates all part prices from GSX"

    def handle(self, *args, **options):
        if len(args) < 1:
            print "Usage: updateprices username [start:finish]"
            sys.exit(1)
        
        start, counter = 0, 0
        finish = 999999999999

        if len(args) == 2:
            start, finish = args[1].split(':')

        GsxAccount.default(User.objects.get(username=args[0]))

        products = Product.objects.filter(pk__gt=start, pk__lt=finish)
        products = products.exclude(part_type='SERVICE')
        products = products.exclude(fixed_price=True)

        for i in products.order_by('id'):
            logging.debug('Updating product %d' % i.pk)
            try:
                i.update_price()
                i.save()
                counter += 1
            except Exception, e:
                logging.debug(e)

        print '%d product prices updated' % counter
