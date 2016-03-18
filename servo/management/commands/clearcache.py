# -*- coding: utf-8 -*-

from django.core.cache import caches
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Clears this install's caches"

    def handle(self, *args, **options):
        for c in caches.all():
            c.clear()

        exit(0)
