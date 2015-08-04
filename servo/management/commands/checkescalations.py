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

from django.db.models import Q
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError

from servo.models import Configuration, Note, User, Escalation


class Command(BaseCommand):
    help = "Check updates for open escalations"

    def handle(self, *args, **options):
        uid = Configuration.conf('imap_act')

        if uid in [None, '']:
            return

        user = User.objects.get(pk=uid)
        tz = timezone.get_current_timezone()
        
        for i in Escalation.objects.exclude(Q(escalation_id='') | Q(status='C')):
            i.gsx_account.connect(i.created_by)
            r = i.get_escalation().lookup()
            aware = timezone.make_aware(r.lastModifiedTimestamp, tz)

            if aware < i.updated_at: # hasn't been updated
                continue

            try:
                parent = i.note_set.latest()
            except Note.DoesNotExist:
                continue

            bodies = [n.body for n in i.note_set.all()]

            for x in r.escalationNotes.iterchildren():
                if x.text in bodies: # skip notes we already have
                    continue

                note = Note(created_by=user, escalation=i, body=x.text)
                parent.add_reply(note)
                note.save()

            i.updated_at = timezone.now()
            i.status = r.escalationStatus
            i.save()
