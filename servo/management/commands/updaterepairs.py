# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from servo.models import Repair


class Command(BaseCommand):

    help = "Updates statuses and details of open GSX repairs"

    def handle(self, *args, **options):
        repairs = Repair.objects.filter(completed_at=None)

        for r in repairs.exclude(confirmation=""):
            r.connect_gsx()
            try:
                details = r.get_details()
                r.update_details(details)
            except Exception:
                pass
