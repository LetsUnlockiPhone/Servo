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
import StringIO
from gsxws import escalations

from django import template
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.forms.models import modelformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import createBarcodeDrawing

from servo.models import Order, Template, Tag, Customer, Note, Attachment, Escalation
from servo.forms import NoteForm, NoteSearchForm, EscalationForm


class BarcodeDrawing(Drawing):
    def __init__(self, text_value, *args, **kwargs):
        barcode = createBarcodeDrawing(
            "Code128",
            value=text_value.encode("utf-8"),
            barHeight=10*mm,
            width=80*mm
        )

        Drawing.__init__(self, barcode.width, barcode.height, *args, **kwargs)
        self.add(barcode, name="barcode")


def show_barcode(request, text):
    """
    Returns text as a barcode
    """
    if request.GET.get('f') == 'svg':
        import barcode
        output = StringIO.StringIO()
        code = barcode.Code39(text, add_checksum=False)
        code.write(output)
        contents = output.getvalue()
        output.close()
        return HttpResponse(contents, content_type="image/svg+xml")

    d = BarcodeDrawing(text)
    return HttpResponse(d.asString("png"), content_type="image/png")


def prep_list_view(request, kind):
    """
    Prepares the view for listing notes/messages
    """
    data = {'title': _("Messages")}
    all_notes = Note.objects.all().order_by("-created_at")

    if kind == "inbox":
        all_notes = all_notes.filter(order=None).order_by("is_read", "-created_at")
    if kind == "sent":
        all_notes = all_notes.filter(created_by=request.user)
    if kind == "flagged":
        all_notes = all_notes.filter(is_flagged=True)
    if kind == "escalations":
        all_notes = Note.objects.all().exclude(escalation=None)

    page = request.GET.get("page")
    paginator = Paginator(all_notes, 20)

    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)

    data['kind'] = kind
    data['notes'] = notes
    data['inbox_count'] = Note.objects.filter(order=None).count()

    return data


@permission_required('servo.change_note')
def copy(request, pk):
    """
    Copies a note with its attachments and labels
    """
    from servo.lib.shorturl import from_time
    note = get_object_or_404(Note, pk=pk)

    new_note = Note(created_by=request.user)
    new_note.body = note.body
    new_note.order = note.order
    new_note.subject = note.subject
    new_note.save()

    new_note.labels = note.labels.all()

    for a in note.attachments.all():
        a.pk = None
        a.content_object = new_note
        a.save()
        new_note.attachments.add(a)

    return redirect(edit, pk=new_note.pk, order_id=note.order_id)


@permission_required('servo.change_note')
def edit(request, pk=None, order_id=None, parent=None, recipient=None, customer=None):
    """
    Edits a note
    """
    to = []
    order = None
    note = Note(order_id=order_id)
    excluded_emails = note.get_excluded_emails()

    if recipient is not None:
        to.append(recipient)

    if order_id is not None:
        order = get_object_or_404(Order, pk=order_id)

        if order.user and (order.user != request.user):
            note.is_read = False
            if order.user.email not in excluded_emails:
                to.append(order.user.email)

        if order.customer is not None:
            customer = order.customer_id

    if customer is not None:
        customer = Customer.objects.get(pk=customer)
        note.customer = customer

        if order_id is None:
            to.append(customer.email)

    tpl = template.Template(note.subject)
    note.subject = tpl.render(template.Context({'note': note}))

    note.recipient = ', '.join(to)
    note.created_by = request.user
    note.sender = note.get_default_sender()

    fields = escalations.CONTEXTS

    try:
        note.escalation = Escalation(created_by=request.user)
    except Exception, e:
        messages.error(request, e)
        return redirect(request.META['HTTP_REFERER'])

    AttachmentFormset = modelformset_factory(Attachment,
                                             fields=('content',),
                                             can_delete=True,
                                             extra=3,
                                             exclude=[])
    formset = AttachmentFormset(queryset=Attachment.objects.none())

    if pk is not None:
        note = get_object_or_404(Note, pk=pk)
        formset = AttachmentFormset(queryset=note.attachments.all())

    if parent is not None:
        parent = Note.objects.get(pk=parent)
        note.parent = parent
        note.body = parent.quote()

        if parent.subject:
            note.subject = _(u'Re: %s') % parent.clean_subject()
        if parent.sender not in excluded_emails:
            note.recipient = parent.sender
        if parent.order:
            order = parent.order
            note.order = parent.order

        note.customer = parent.customer
        note.escalation = parent.escalation
        note.is_reported = parent.is_reported

    title = note.subject
    form = NoteForm(instance=note)

    if note.escalation:
        contexts = json.loads(note.escalation.contexts)

    escalation_form = EscalationForm(prefix='escalation', instance=note.escalation)

    if request.method == "POST":
        escalation_form = EscalationForm(request.POST,
                                         prefix='escalation',
                                         instance=note.escalation)

        if escalation_form.is_valid():
            note.escalation = escalation_form.save()

        form = NoteForm(request.POST, instance=note)

        if form.is_valid():

            note = form.save()
            formset = AttachmentFormset(request.POST, request.FILES)

            if formset.is_valid():

                files = formset.save(commit=False)

                for f in files:
                    f.content_object = note
                    try:
                        f.save()
                    except ValueError, e:
                        messages.error(request, e)
                        return redirect(note)

                note.attachments.add(*files)
                note.save()

                try:
                    msg = note.send_and_save(request.user)
                    messages.success(request, msg)
                except ValueError, e:
                    messages.error(request, e)

            return redirect(note)

    return render(request, "notes/form.html", locals())


def delete_note(request, pk):
    """
    Deletes a note
    """
    note = get_object_or_404(Note, pk=pk)

    if request.method == 'POST':
        note.delete()
        messages.success(request, _("Note deleted"))

        if request.session.get('return_to'):
            url = request.session.get('return_to')
            del(request.session['return_to'])
        elif note.order_id:
            url = note.order.get_absolute_url()

        return redirect(url)

    return render(request, 'notes/remove.html', {'note': note})


@csrf_exempt
def render_template(request):
    """
    Renders the template with this title with the current
    Service Order as the context
    """
    content = ''
    title = request.POST.get('title')
    tpl = Template.objects.get(title=title)

    if request.session.get('current_order_id'):
        tpl = template.Template(tpl.content)
        order = Order.objects.get(pk=request.session['current_order_id'])
        content = tpl.render(template.Context({'order': order}))

    return HttpResponse(content)


def templates(request, template_id=None):
    if template_id is not None:
        tpl = Template.objects.get(pk=template_id)
        content = tpl.content
        if request.session.get('current_order_id'):
            tpl = template.Template(content)
            order = Order.objects.get(pk=request.session['current_order_id'])
            content = tpl.render(template.Context({'order': order}))

        return HttpResponse(content)

    templates = Template.objects.all()
    return render(request, 'notes/templates.html', {'templates': templates})


def toggle_flag(request, pk, flag):
    field = 'is_%s' % flag
    note = Note.objects.get(pk=pk)
    attr = getattr(note, field)
    setattr(note, field, not attr)
    note.save()

    return HttpResponse(getattr(note, 'get_%s_title' % flag)())


def toggle_tag(request, pk, tag_id):
    note = Note.objects.get(pk=pk)
    tag = Tag.objects.get(pk=tag_id)

    if tag in note.labels.all():
        note.labels.remove(tag)
    else:
        note.labels.add(tag)

    if note.order:
        return redirect(note.order)

    return HttpResponse(_('OK'))

def list_notes(request, kind="inbox"):
    data = prep_list_view(request, kind)
    request.session['return_to'] = request.path
    return render(request, "notes/list_notes.html", data)


def view_note(request, kind, pk):
    note = Note.objects.get(pk=pk)
    data = prep_list_view(request, kind)
    data['title'] = note.subject
    data['note'] = note

    if kind == 'escalations':
        return render(request, "notes/view_escalation.html", data)
    else:
        return render(request, "notes/view_note.html", data)


def search(request):
    query = request.GET.get("q")
    request.session['search_query'] = query

    title = _(u'Notes containing "%s"') % query
    results = Note.objects.filter(body__icontains=query).order_by('-created_at')
    paginator = Paginator(results, 10)

    page = request.GET.get("page")

    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)

    return render(request, "notes/search.html", locals())


def find(request):
    form = NoteSearchForm(request.GET)
    results = Note.objects.none()

    if request.GET and form.is_valid():

        fdata = form.cleaned_data
        results = Note.objects.all()

        if fdata.get('body'):
            results = results.filter(body__icontains=fdata['body'])
        if fdata.get('recipient'):
            results = results.filter(recipient__icontains=fdata['recipient'])
        if fdata.get('sender'):
            results = results.filter(sender__icontains=fdata['sender'])
        if fdata.get('order_code'):
            results = results.filter(order__code__icontains=fdata['order_code'])

        results = results.order_by('-created_at')

    paginator = Paginator(results, 10)
    page = request.GET.get("page")

    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)

    title = _('Message search')
    return render(request, "notes/find.html", locals())


def edit_escalation(request):
    pass


def create_escalation(request):
    esc = Escalation()
    form = EscalationForm()
    title = _('Edit Escalation')

    if request.method == 'POST':
        data = request.POST.copy()
        data['created_by'] = request.user
        form = EscalationForm(data, request.FILES, instance=esc)
        if form.is_valid():
            note = form.save()
            #esc.submit(request.user)
            return redirect(view_note, 'escalations', note.pk)

    return render(request, 'notes/edit_escalation.html', locals())


def list_messages(request, pk):
    note = get_object_or_404(Note, pk=pk)
    messages = note.message_set.all()
    return render(request, "notes/messages.html", locals())
