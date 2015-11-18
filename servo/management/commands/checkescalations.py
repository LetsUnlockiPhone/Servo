# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError

from servo.lib.utils import empty
from servo.exceptions import ConfigurationError
from servo.models import Configuration, Note, User, Escalation


class Command(BaseCommand):
    help = "Check updates for open escalations"

    def handle(self, *args, **options):
        # get local user to create notes as
        uid = Configuration.conf('imap_act')
        
        if empty(uid):
            raise ConfigurationError('Incoming message user not defined')

        user = User.objects.get(pk=uid)
        tz = timezone.get_current_timezone()
        
        for i in Escalation.objects.exclude(Q(escalation_id='') | Q(status='C')):
            # connect per-user since the escalations can be under different ship-tos
            try:
                i.gsx_account.connect(i.created_by)
            except Exception:
                continue # skip auth errors so we don't get stuck

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
