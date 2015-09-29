# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from time import strftime
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backup this Servo database'

    def handle(self, *args, **options):
        db  = settings.DATABASES['default']
        fn = '%s_%s.pgdump' % (db['NAME'], strftime('%Y%m%d_%H%I'))
        fn = os.path.join(settings.BACKUP_DIR, fn)

        subprocess.call(['/Applications/Postgres.app/Contents/Versions/9.3/bin/pg_dump', '-Fc', db['NAME'], '-U', db['USER'], 
             '-f' , fn], env={'PGPASSWORD': db['PASSWORD']})
