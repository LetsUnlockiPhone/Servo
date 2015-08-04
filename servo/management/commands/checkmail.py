# -*- coding: utf-8 -*-
# Copyright (c) 2013, First Party Software
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
# SUCH DAMAGE.

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
