# -*- coding: utf-8 -*-

import logging
from email.parser import Parser

from django.core.management.base import BaseCommand

from servo.models import Configuration, Note, User


class Command(BaseCommand):
    help = "Checks IMAP box for new mail"

    def handle(self, *args, **options):
        uid = Configuration.conf('imap_act')

        if uid == '':
            raise ValueError('Incoming message user not configured')

        user = User.objects.get(pk=uid)
        server = Configuration.get_imap_server()
        typ, data = server.search(None, "UnSeen")

        for num in data[0].split():
            #logging.debug("** Processing message %s" % num)
            typ, data = server.fetch(num, "(RFC822)")
            # parsestr() seems to return an email.message?
            msg = Parser().parsestr(data[0][1])
            Note.from_email(msg, user)
            #server.copy(num, 'servo')
            server.store(num, '+FLAGS', '\\Seen')

        server.close()
        server.logout()
