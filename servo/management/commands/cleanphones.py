# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from servo.models import Customer


class Command(BaseCommand):
    help = "Cleans illegal characters from phone numbers"

    def handle(self, *args, **options):
        ALLOWED_CHARS = r'^[\d\s\+\-]+$'
        for i in Customer.objects.exclude(phone__regex=ALLOWED_CHARS):
            if i.phone == '':
                continue
                
            i.notes = i.notes + i.phone
            i.phone = ''
            i.save()
