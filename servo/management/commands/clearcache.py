# -*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Clears this install's cache"

    def handle(self, *args, **options):
        cache.clear()
