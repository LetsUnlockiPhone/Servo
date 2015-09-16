# -*- coding: utf-8 -*-

import os
import Image
import logging
from glob import glob
from django.core.management.base import BaseCommand

from servo.models import Attachment


class Command(BaseCommand):

    help = "Does various cleanup"

    def handle(self, *args, **options):
        size = 128, 128
        logging.info("Building avatar thumbnails")
        for infile in glob("servo/uploads/avatars/*.jpg"):
            logging.info(infile)
            im = Image.open(infile)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(infile, "JPEG")

        logging.info("Cleaning up unused attachments")
        for infile in glob("servo/uploads/attachments/*"):
            fn = infile.decode('utf-8')
            fp = os.path.join("attachments", os.path.basename(fn))
            try:
                Attachment.objects.get(content=fp)
            except Attachment.DoesNotExist:
                os.remove(infile)
