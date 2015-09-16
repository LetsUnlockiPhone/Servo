# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from servo.models import Order


class Command(BaseCommand):

    help = "Updates order descriptions"

    def handle(self, *args, **options):
        for o in Order.objects.filter(description=""):
            o.description = o.device_name() or ""
            o.save()

        for o in Order.objects.filter(status_name=""):
            o.status_name = o.get_status_name() or ""
            o.save()

        for o in Order.objects.filter(customer_name=""):
            o.customer_name = o.get_customer_name() or ""
            o.save()
