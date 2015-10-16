# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from servo.lib import ucsv
from servo.models import Product


class Command(BaseCommand):

    help = "Update product prices from CSV file"

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        """
        CODE
        NAME
        DESCRIPTION
        PRICE_EXCHANGE
        """
        f = open(options['path'][0], 'rUb')
        raw = ucsv.read_excel_file(f)
        clean = [r for r in raw if r[0] != '']

        for i in clean:
            print i
