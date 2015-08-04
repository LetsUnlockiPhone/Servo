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

import os
import csv
import shutil
import subprocess
from datetime import date
from django.db import connection

from django.core.management.base import BaseCommand


def write(path, header, cursor):
    with open(path, 'w') as fout:
        writer = csv.writer(fout)
        writer.writerow(header)

        for row in cursor.fetchall():
            row = [unicode(s).encode('utf-8') for s in row]
            writer.writerow(row)


class Command(BaseCommand):

    help = 'Export this servo database in a portable format'
    
    def handle(self, *args, **options):
        backupdir = 'backups/%s' % date.today().isoformat()
        os.mkdir(backupdir)

        cursor = connection.cursor()        
        
        path = os.path.join(backupdir, 'notes.csv')
        cursor.execute("""SELECT id, order_id, created_by_id, created_at, body 
            FROM servo_note""")
        header = ['ID', 'ORDER_ID', 'USER_ID', 'CREATED_AT', 'NOTE']
        write(path, header, cursor)

        path = os.path.join(backupdir, 'users.csv')
        header = ['ID', 'USERNAME', 'FIRST_NAME', 'LAST_NAME', 'EMAIL']
        cursor.execute("""SELECT id, username, first_name, last_name, email 
            FROM servo_user WHERE is_visible = TRUE""")
        write(path, header, cursor)

        path = os.path.join(backupdir, 'orders.csv')
        header = ['ID', 'CODE', 'CREATED_AT', 
            'CLOSED_AT', 'CUSTOMER_ID', 'USER_ID', 'QUEUE_ID']
        cursor.execute("""SELECT id, code, created_at, closed_at, 
            customer_id, user_id, queue_id 
            FROM servo_order""")
        write(path, header, cursor)

        path = os.path.join(backupdir, 'queues.csv')
        header = ['ID', 'NAME', 'DESCRIPTION', 
            'CLOSED_AT', 'CUSTOMER_ID', 'USER_ID', 'QUEUE_ID']
        cursor.execute("""SELECT id, title, description FROM servo_queue""")
        write(path, header, cursor)

        path = os.path.join(backupdir, 'devices.csv')
        header = ['ID', 'SERIAL_NUMBER', 'IMEI', 
        'CONFIGURATION', 'WARRANTY_STATUS', 'PURCHASE_DATE', 'NOTES']
        cursor.execute("""SELECT id, sn, imei, configuration, warranty_status,
        purchased_on, notes FROM servo_device""")
        write(path, header, cursor)

        path = os.path.join(backupdir, 'repairs.csv')
        header = ['ID', 'ORDER_ID', 'DEVICE_ID', 'USER_ID',
            'SUBMITTED_AT', 'COMPLETED_AT', 'REQUEST_REVIEW', 
            'TECH_ID', 'UNIT_RECEIVED', 'CONFIRMATION', 
            'REFERENCE', 'SYMPTOM', 'DIAGNOSIS', 'NOTES']
        cursor.execute("""SELECT id, order_id, device_id, 
            created_by_id, submitted_at, completed_at, 
            request_review, tech_id, unit_received_at, confirmation, reference,
            symptom, diagnosis, notes
            FROM servo_repair
            WHERE submitted_at IS NOT NULL""")
        write(path, header, cursor)

        header = ['ID', 'CODE', 'TITLE', 'DESCRIPTION', 
        'PRICE_PURCHASE_EXCHANGE', 'PRICE_PURCHASE_STOCK',
        'PRICE_SALES_EXCHANGE', 'PRICE_SALES_STOCK', 'COMPONENT_CODE',
        'PART_TYPE', 'EEE_CODE']
        cursor.execute("""SELECT id, code, title, description,
            price_purchase_exchange, price_purchase_stock,
            price_sales_exchange, price_sales_stock,
            component_code, part_type, eee_code
            FROM servo_product""")
        path = os.path.join(backupdir, 'products.csv')
        write(path, header, cursor)

        header = ['ID', 'PARENT_ID', 'NAME', 'PHONE', 'EMAIL',
        'STREET_ADDRESS', 'POSTAL_CODE', 'CITY'
        'COUNTRY', 'NOTES']
        cursor.execute("""SELECT id, parent_id, name, phone,
            email, street_address, zip_code, city, country, notes
            FROM servo_customer""")
        path = os.path.join(backupdir, 'customers.csv')
        write(path, header, cursor)

        path = os.path.join(backupdir, 'order_products.csv')
        header = ['ID', 'PRODUCT_ID', 'ORDER_ID', 'CODE', 'TITLE',
        'DESCRIPTION', 'AMOUNT', 'SERIAL_NUMBER', 'KBB_SN',
        'IMEI', 'REPORTED', 'PRICE_CATEGORY', 'PRICE'
        'COMPTIA_CODE', 'COMPTIA_MODIFIER']
        cursor.execute("""SELECT id, product_id, order_id, code,
            title, description, amount, sn, price, kbb_sn,
            imei, should_report, price_category, price,
            comptia_code, comptia_modifier
            FROM servo_serviceorderitem""")
        write(path, header, cursor)

        path = os.path.join(backupdir, 'parts.csv')
        header = ['ID', 'REPAIR_ID', 'ORDER_ITEM_ID',
        'NUMBER', 'TITLE', 'COMPTIA_CODE', 'COMPTIA_MODIFIER',
        'RETURN_ORDER', 'RETURN_STATUS', 'RETURN_CODE',
        'ORDER_STATUS', 'COVERAGE', 'SHIP_TO', 'RETURNED_AT']
        cursor.execute("""SELECT id, repair_id, order_item_id,
            part_number, part_title, comptia_code, comptia_modifier,
            return_order, return_status,  return_code,
            order_status, coverage_description, ship_to, returned_at
            FROM servo_servicepart""")
        write(path, header, cursor)

        path = os.path.join(backupdir, 'order_devices.csv')
        header = ['ID', 'ORDER_ID', 'DEVICE_ID', 'REPORTED']
        cursor.execute("""SELECT id, order_id, device_id, should_report
            FROM servo_orderdevice""")
        write(path, header, cursor)

        subprocess.call(['tar', '-C', backupdir, '-zcf', '%s.tar.gz' % backupdir, '.'])
        shutil.rmtree(backupdir, ignore_errors=True)
