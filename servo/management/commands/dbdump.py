# -*- coding: utf-8 -*-

import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Dumps DB of this instance to specified file"

    def handle(self, *args, **options):
        dbname = settings.DATABASES['default']['NAME']
        #subprocess.call('pg_dump', '-Fc',  dbname, '-U', 'pgsql' > "${BACKUPDIR}/${db}_$(date "+%Y%m%d_%H%M").pgdump"
