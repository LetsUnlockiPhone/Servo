# -*- coding: utf-8 -*-

import sys
import logging
import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backup this Servo database'
    def handle(self, *args, **options):
        if len(args) < 1:
            print 'Usage: dbbackup file'
            sys.exit(1)
        db  = settings.DATABASES['default']
        pg_dump = subprocess.check_output(['which', 'pg_dump']).strip()
        subprocess.call([pg_dump, '-Fc', db['NAME'], '-U', db['USER'], 
                        '-f' , args[0]], env={'PGPASSWORD': db['PASSWORD']})
