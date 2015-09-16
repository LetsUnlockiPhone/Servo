# -*- coding: utf-8 -*-

import logging
from email.parser import Parser

from django.core.management.base import BaseCommand, CommandError

from servo.models import User


class Command(BaseCommand):
    help = "Converts SuperUsers to Staff"

    def handle(self, *args, **options):
        for u in User.objects.filter(is_superuser=True):
            u.is_superuser = False
            u.is_staff = True
            u.save()
            