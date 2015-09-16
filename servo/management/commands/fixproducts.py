# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from servo.models import ServiceOrderItem, Product


class Command(BaseCommand):
    help = "Fixes SOI and Product codes that include spaces"

    def handle(self, *args, **options):
        for i in Product.objects.filter(code__contains=' '):
            i.code = slugify(i.code)
            i.save()

        for i in ServiceOrderItem.objects.filter(code__contains=' '):
            i.code = slugify(i.code)
            i.save()
