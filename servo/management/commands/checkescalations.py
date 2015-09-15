# -*- coding: utf-8 -*-

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
