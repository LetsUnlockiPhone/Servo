# -*- coding: utf-8 -*-

import os.path
from subprocess import call
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Updates this Servo installation"

    def handle(self, *args, **options):
        mc = os.path.join(settings.BASE_DIR, 'manage.py')
        call(['git', 'pull', 'origin', 'master'])
        call([mc, 'migrate', '--no-initial-data'])
        call([mc, 'clearsessions'])
