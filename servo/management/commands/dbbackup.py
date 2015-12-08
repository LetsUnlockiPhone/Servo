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
        if not os.path.exists(settings.BACKUP_DIR):
            os.mkdir(settings.BACKUP_DIR)
        fn = os.path.join(settings.BACKUP_DIR, fn)
        env = {'PATH': os.getenv('PATH'), 'PGPASSWORD': db['PASSWORD']}
        subprocess.call(['pg_dump', '-Fc', db['NAME'], '-U',
                        db['USER'], '-f' , fn], env=env)
