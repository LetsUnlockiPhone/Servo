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

import json
import gsxws
from gsxws.escalations import Context

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from servo import defaults
from servo.models import GsxAccount, User, Attachment


class Escalation(models.Model):
    """
    Escalation/Note
    """
    escalation_id = models.CharField(
        default='',
        max_length=22,
        editable=False
    )
    gsx_account = models.ForeignKey(
        GsxAccount,
        default=defaults.gsx_account,
        verbose_name=_('GSX Account'),
    )
    contexts = models.TextField(default='{}', blank=True)
    issue_type = models.CharField(
        default='',
        blank=True,
        max_length=4,
        choices=gsxws.escalations.ISSUE_TYPES
    )
    status = models.CharField(
        max_length=1,
        choices=gsxws.escalations.STATUSES,
        default=gsxws.escalations.STATUS_OPEN
    )
    submitted_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, editable=False, null=True)

    def is_submitted(self):
        return self.submitted_at is not None

    def to_gsx(self):
        self.gsx_account.connect(self.created_by)
        esc = gsxws.escalations.Escalation()

        note = self.note_set.latest()
        esc.notes = note.body

        try:
            attachment = note.attachments.latest()
            f = attachment.content.file.name
            a = gsxws.escalations.FileAttachment(f)
            esc.attachment = a
        except Attachment.DoesNotExist:
            pass

        return esc

    def get_escalation(self):
        esc = gsxws.escalations.Escalation()
        esc.escalationId = self.escalation_id
        return esc

    def update(self, note):
        esc = self.to_gsx()
        esc.escalationId = self.escalation_id
        esc.status = self.status
        
        return esc.update()

    def submit(self):
        esc = self.to_gsx()
        esc.shipTo = self.gsx_account.ship_to
        esc.issueTypeCode = self.issue_type

        if len(self.contexts) > 2:
            ec = []
            for k, v in json.loads(self.contexts).items():
                ec.append(Context(k, v))

            esc.escalationContext = ec

        result = esc.create()
        self.submitted_at = timezone.now()
        self.escalation_id = result.escalationId

        self.save()

    @property
    def subject(self):
        return _(u'Escalation %s') % self.escalation_id

    class Meta:
        app_label = "servo"

