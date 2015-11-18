# -*- coding: utf-8 -*-

import os
import os.path
import subprocess
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Dumps DB of this instance to specified file"

    def handle(self, *args, **options):
        s = settings.DATABASES['default']
        db, user, pw = s['NAME'], s['USER'], s['PASSWORD']
        fname  = datetime.now().strftime('%Y%m%d_%H%M') + '.pgdump'
        path = os.path.join(settings.BACKUP_DIR, fname)
        os.putenv('PGPASSWORD', pw)
        subprocess.call(['pg_dump', '-Fc',  db, '-U', user, '-f', path])
