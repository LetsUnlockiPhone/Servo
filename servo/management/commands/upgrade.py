# -*- coding: utf-8 -*-

import subprocess
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Upgrade requirements"

    def handle(self, *args, **options):
        subprocess.call(['pip', 'install', '-U', '-r', 'requirements.pip'])
