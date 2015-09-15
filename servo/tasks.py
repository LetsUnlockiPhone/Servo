# -*- coding: utf-8 -*-

from __future__ import absolute_import

from celery import shared_task

from django.core.cache import cache

from servo.models import Order, Note


def get_rules():
	import json
	fh = open("local_rules.json", "r")
	rules = json.load(fh)
	cache.set('rules', rules)
	return rules


@shared_task
def apply_rules(event):

	rules = cache.get('rules', get_rules())

	for r in rules:
		if (r['event'] == event.action) and (r['match'] == event.description):

			if r['action'] == "set_queue":
				order = event.content_object
				order.set_queue(r['data'], event.triggered_by)

			if r['action'] == "send_sms":
				number = 0
				order = event.content_object

				try:
					number = order.customer.get_standard_phone()
				except Exception as e:
					continue

				note = Note(order=order, created_by=event.triggered_by)

				note.body = r['data']
				note.render_body({'order': order})
				note.save()

				return note.send_sms(number, event.triggered_by)


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

