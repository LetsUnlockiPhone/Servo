# -*- coding: utf-8 -*-

from django.db import models
from django.core.cache import cache

from django.dispatch import receiver
from django.db.models.signals import post_save

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from servo.models import Event, Queue


class ServoModel(models.Model):
    class Meta:
        abstract = True
        app_label = "servo"


class Rule(ServoModel):
    description = models.CharField(max_length=128, default=_('New Rule'))
    MATCH_CHOICES = (
        ('ANY', _('Any')),
        ('ALL', _('All')),
    )
    match = models.CharField(
        max_length=3,
        default='ANY',
        choices=MATCH_CHOICES
    )

    def as_dict(self):
        d = {'description': self.description}
        d['match'] = self.match
        return d

    def serialize(self):
        """
        Returns this rule as a JSON-string
        """
        import json
        d = self.as_dict()
        d['conditions'] = []
        d['actions'] = []

        for i in self.condition_set.all():
            d['conditions'].append(i.as_dict())

        for i in self.action_set.all():
            d['actions'].append(i.as_dict())

        return json.dumps(d)


    def get_name(self):
        return self.description

    def get_admin_url(self):
        return reverse('rules-edit_rule', args=[self.pk])

    def apply(self, event):
        order = event.content_object
        for a in self.action_set.all():
            a.apply(order, event)

    def __unicode__(self):
        return self.description


class Condition(ServoModel):
    rule = models.ForeignKey(Rule)

    EVENT_MAP = {
        'device_added': 'DEVICE',
    }

    KEY_CHOICES = (
        ('QUEUE',         _('Queue')),
        ('STATUS',        _('Status')),
        ('DEVICE',        _('Device name')),
        ('CUSTOMER_NAME', _('Customer name')),
    )

    key = models.CharField(max_length=16, choices=KEY_CHOICES)
    OPERATOR_CHOICES = (
        ('^%s$',    _('Equals')),
        ('%s',      _('Contains')),
        ('%d < %d', _('Less than')),
        ('%d > %d', _('Greater than')),
    )
    operator = models.CharField(
        max_length=4,
        default='^%s$',
        choices=OPERATOR_CHOICES
    )
    value = models.TextField(default='')

    def as_dict(self):
        d = {'key': self.key}
        d['operator'] = self.operator
        d['value'] = self.value
        return d

    def __unicode__(self):
        return '%s %s %s' % (self.key, self.operator, self.value)


class Action(ServoModel):
    rule = models.ForeignKey(Rule)

    KEY_CHOICES = (
        ('SEND_SMS',    _('Send SMS')),
        ('SEND_EMAIL',  _('Send email')),
        ('ADD_TAG',     _('Add Tag')),
        ('SET_PRIO',    _('Set Priority')),
        ('SET_QUEUE',   _('Set Queue')),
        ('SET_USER',    _('Assign to')),
    )

    key = models.CharField(
        max_length=32,
        default='SEND_EMAIL',
        choices=KEY_CHOICES
    )
    value = models.TextField(default='')

    def as_dict(self):
        d = {'key': self.key}
        d['value'] = self.value
        return d

    def apply(self, order, event):
        if self.key == 'SET_QUEUE':
            order.set_queue(self.value, event.triggered_by)

        if self.key == 'SET_USER':
            order.set_user(self.value, event.triggered_by)

    def __unicode__(self):
        return '%s %s' % (self.key, self.value)


@receiver(post_save, sender=Event)
def process_event(sender, instance, created, **kwargs):
    try:
        condition = Condition.EVENT_MAP[instance.action]
        print condition
        for r in Rule.objects.filter(condition__key=condition):
            print 'APPLYING %s' % condition
            r.apply(instance)
    except KeyError:
        return # no mapping for this event
