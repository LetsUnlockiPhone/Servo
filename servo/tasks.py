# -*- coding: utf-8 -*-

from __future__ import absolute_import

from email.parser import Parser

from celery import shared_task

from django.conf import settings
from django.core.cache import cache

from servo.lib.utils import empty
from servo.exceptions import ConfigurationError
from servo.models import Configuration, User, Order, Note, Template


def get_rules():
    """Get the rules from the JSON file and cache them.
    Fail silently if not configured.

    @FIXME: Need GUI for managing local_rules.json!
    """
    import json

    try:
        fh = open("local_rules.json", "r")
    except IOError:
        return []
        
    rules = json.load(fh)
    cache.set('rules', rules)
    return rules


@shared_task
def apply_rules(event):
    """Applies configured rules

    event is the Event object that was triggered
    """
    counter = 0
    rules = cache.get('rules', get_rules())
    order = event.content_object
    user  = event.triggered_by

    for r in rules:
        match = r.get('match', event.description)

        if (r['event'] == event.action and match == event.description):
            if isinstance(r['data'], dict):
                tpl_id = r['data']['template']
                r['data'] = Template.objects.get(pk=tpl_id).render(order)

            if r['action'] == "set_queue":
                order.set_queue(r['data'], user)

            if r['action'] == "set_priority":
                pass

            if r['action'] == "send_email":
                try:
                    email = order.customer.valid_email()
                except Exception:
                    continue # skip customers w/o valid emails
                
                note = Note(order=order, created_by=user)
                note.body = r['data']
                note.recipient = email
                note.render_subject({'note': note})
                note.save()

                try:
                    note.send_mail(user)
                except ValueError as e:
                    print('Sending email failed (%s)' % e)

            if r['action'] == "send_sms":
                number = 0

                try:
                    number = order.customer.get_standard_phone()
                except Exception:
                    continue # skip customers w/o valid phone numbers

                note = Note(order=order, created_by=user)

                note.body = r['data']
                note.save()

                try:
                    note.send_sms(number, user)
                except ValueError as e:
                    print('Sending SMS to %s failed (%s)' % (number, e))

            counter += 1

    return '%d/%d rules processed' % (counter, len(rules))


@shared_task
def batch_process(user, data):
    """
    /orders/batch
    """
    processed = 0
    orders = data['orders'].strip().split("\r\n")
    
    for o in orders:
        try:
            order = Order.objects.get(code=o)
        except Exception as e:
            continue

        if data['status'] and order.queue:
            status = order.queue.queuestatus_set.get(status_id=data['status'])
            order.set_status(status, user)
        
        if data['queue']:
            order.set_queue(data['queue'], user)

        if len(data['sms']) > 0:
            try:
                number = order.customer.get_standard_phone()
                note = Note(order=order, created_by=user, body=data['sms'])
                note.render_body({'order': order})
                note.save()

                try:
                    note.send_sms(number, user)
                except Exception as e:
                    note.delete()
                    print("Failed to send SMS to: %s" % number)

            except AttributeError as e: # customer has no phone number
                continue

        if len(data['email']) > 0:
            note = Note(order=order, created_by=user, body=data['email'])
            note.sender = user.email

            try:
                note.recipient = order.customer.email
                note.render_subject({'note': note})
                note.render_body({'order': order})
                note.save()
                note.send_mail(user)
            except Exception as e:
                # customer has no email address or some other error...
                pass

        if len(data['note']) > 0:
            note = Note(order=order, created_by=user, body=data['note'])
            note.render_body({'order': order})
            note.save()

        processed += 1

    return '%d/%d orders processed' % (processed, len(orders))


@shared_task
def check_mail():
    """Checks IMAP box for incoming mail"""
    uid = Configuration.conf('imap_act')

    if empty(uid):
        raise ConfigurationError('Incoming message user not configured')

    counter = 0
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
        counter += 1

    server.close()
    server.logout()

    return '%d messages processed' % counter
