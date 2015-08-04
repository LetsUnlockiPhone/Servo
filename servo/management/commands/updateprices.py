# -*- coding: utf-8 -*-
# Copyright (c) 2013, First Party Software
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
# SUCH DAMAGE.

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
