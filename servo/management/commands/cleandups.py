# -*- coding: utf-8 -*-

import logging
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from servo.models import TaggedItem


class Command(BaseCommand):

    help = "Cleans various duplicate data"

    def handle(self, *args, **options):
        logging.info("Cleaning up duplicate tags")
        for d in TaggedItem.objects.filter(slug=None):
            d.slug = slugify(d.description)
            d.save()
