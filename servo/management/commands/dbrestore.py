# -*- coding: utf-8 -*-

import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
     help = 'Restore this Servo database from backup'
     def handle(self, *args, **options):
          if len(args) < 1:
               print 'Usage: dbrestore file'
               sys.exit(1)

          db = settings.DATABASES['default']
          pg_restore = subprocess.check_output(['which', 'pg_restore']).strip()
          subprocess.call([pg_restore, '-d', db['NAME'], '-O', '-x', '-U', db['USER'],
                          args[0]], env={'PGPASSWORD': db['PASSWORD']})
