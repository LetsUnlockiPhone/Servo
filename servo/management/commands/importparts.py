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

import re
import os
import logging

from decimal import Decimal, InvalidOperation, ROUND_CEILING

from django.db import DatabaseError
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from servo.models import Product, TaggedItem


class Command(BaseCommand):

    help = "Imports complete GSX parts database"

    def handle(self, *args, **options):

        update_prices = True
        import_vintage = True
        dbpath = "servo/uploads/products/partsdb.csv"

        try:
            partsdb = open(dbpath, "r")
        except Exception:
            pass

        content_type = ContentType.objects.get(model="product")

        for l in partsdb.readlines():

            line = l.decode("iso-8859-1")
            row = line.strip().split("\t")

            if row[5] == "" or row[5] == "Currency":
                continue  # Skip header row and rows without currency

            logging.debug(row)

            category = row[0]

            if re.match(r'~VIN', category) and not import_vintage:
                continue  # Skip vintage devices if so desired

            p_number = row[1]

            if re.match(r'675-', p_number):
                continue  # Skip DEPOT REPAIR INVOICE

            p_title = row[2]
            p_type = row[3]
            lab_tier = row[4]

            try:
                stock_price = Decimal(row[6])
            except InvalidOperation:
                continue  # Skip parts with no stock price

            exchange_price = Decimal(row[7])

            eee_code = row[8]

            # skip substitute
            component_group = row[10] or None
            is_serialized = row[11]
            req_diag = (row[12] == "Y")

            product, created = Product.objects.get_or_create(code=p_number)

            product.title = p_title
            product.eee_code = eee_code
            product.labour_tier = lab_tier
            product.part_type = p_type or "OTHER"

            product.component_code = component_group
            product.is_serialized = (is_serialized == "Y")

            if update_prices:
                if stock_price:
                    purchase_sp = Decimal(stock_price)
                    product.price_purchase_stock = purchase_sp.to_integral_exact(rounding=ROUND_CEILING)
                    product.set_stock_sales_price()

                if exchange_price:
                    purchase_ep = Decimal(exchange_price)
                    product.price_purchase_exchange = purchase_ep.to_integral_exact(rounding=ROUND_CEILING)
                    product.set_exchange_sales_price()

            product.save()

            try:
                tag, created = TaggedItem.objects.get_or_create(
                    content_type=content_type,
                    object_id=product.pk,
                    tag=category)
                tag.save()
            except DatabaseError:
                pass

        os.unlink(dbpath)
