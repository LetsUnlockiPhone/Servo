# -*- coding: utf-8 -*-

import logging
from django.core.management.base import BaseCommand

from servo.models import (Order, Repair,)

class Command(BaseCommand):
    help = "Deletes orders listed in text file"

    def handle(self, *args, **options):
        if len(args) < 1:
            print 'Usage: deleteorders data.txt'
            sys.exit(1)

        counter = 0
        dataf = open(args[0], 'r')

        for l in dataf.readlines():
            cols = l.strip().split("\t")
            try:
                print 'Deleting order %s' % cols[0]
                order = Order.objects.get(code=cols[0])
                Repair.objects.filter(order=order).delete()
                order.delete()
                counter += 1
            except Order.DoesNotExist:
                pass
            
        print '%d orders deleted' % counter
