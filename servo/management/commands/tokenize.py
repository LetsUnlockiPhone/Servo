# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError

from servo.models import User


class Command(BaseCommand):
    help = "Creates API token for user"

    def handle(self, *args, **options):
        user = User.objects.get(username=args[0])
        print(user.create_token())
