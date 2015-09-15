# -*- coding: utf-8 -*-

import gsxws

from django.db import IntegrityError, transaction

from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from django.conf import settings as app_settings
from django.utils.translation import ugettext as _

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group

from django.forms.models import (inlineformset_factory,
                                modelform_factory,
                                modelformset_factory,)

from servo.forms.admin import *
from servo.models.common import *
from servo.models.repair import Checklist, ChecklistItem
from servo.models.account import User, Group
from servo.models.product import ShippingMethod


def prep_list_view(model):
    title = model._meta.verbose_name_plural
    object_list = model.objects.all()
    return locals()


@staff_member_required
def list_gsx_accounts(request):
    object_list = GsxAccount.objects.all()
    title = GsxAccount._meta.verbose_name_plural

    if object_list.count() > 0:
        return redirect(object_list[0].get_admin_url())

    return render(request, 'admin/gsx/index.html', locals())


@staff_member_required
def edit_gsx_account(request, pk=None):
    object_list = GsxAccount.objects.all()
    title = GsxAccount._meta.verbose_name_plural

    if pk is None:
        act = GsxAccount()
    else:
        act = GsxAccount.objects.get(pk=pk)

    form = GsxAccountForm(instance=act)

    if request.method == 'POST':
        form = GsxAccountForm(request.POST, instance=act)
        if form.is_valid():
            try:
                act = form.save()
                cache.delete('gsx_session')
                try:
                    act.test()
                    messages.success(request, _(u'%s saved') % act.title)
                    return redirect(list_gsx_accounts)
                except gsxws.GsxError, e:
                    messages.warning(request, e)
            except IntegrityError:
                transaction.rollback()
                msg = _('GSX account for this sold-to and environment already exists')
                messages.error(request, msg)

    return render(request, 'admin/gsx/form.html', locals())


@staff_member_required
def delete_gsx_account(request, pk=None):
    act = GsxAccount.objects.get(pk=pk)
    if request.method == 'POST':
        try:
            act.delete()
            messages.success(request, _("GSX account deleted"))
        except Exception, e:
            messages.error(request, e)

        return redirect(list_gsx_accounts)

    return render(request, 'admin/gsx/remove.html', {'action': request.path})


@staff_member_required
def checklists(request):
    object_list = Checklist.objects.all()
    title = Checklist._meta.verbose_name_plural

    if object_list.count() > 0:
        return redirect(object_list[0].get_admin_url())

    return render(request, 'admin/checklist/index.html', locals())


@staff_member_required
def edit_checklist(request, pk=None):
    object_list = Checklist.objects.all()
    title = Checklist._meta.verbose_name_plural
    ChecklistItemFormset = inlineformset_factory(Checklist, ChecklistItem, exclude=[])

    if pk is None:
        checklist = Checklist()
    else:
        checklist = Checklist.objects.get(pk=pk)

    form = ChecklistForm(instance=checklist)
    formset = ChecklistItemFormset(instance=checklist)

    if request.method == 'POST':
        form = ChecklistForm(request.POST, instance=checklist)

        if form.is_valid():
            checklist = form.save()
            formset = ChecklistItemFormset(request.POST, instance=checklist)

            if formset.is_valid():
                formset.save()
                messages.success(request, _('Checklist saved'))
                return redirect(checklist.get_admin_url())

    return render(request, 'admin/checklist/form.html', locals())


@staff_member_required
def delete_checklist(request, pk):
    checklist = Checklist.objects.get(pk=pk)

    if request.method == 'POST':
        checklist.delete()
        messages.success(request, _('Checklist deleted'))
        return redirect(checklists)

    action = str(request.path)
    title = _('Really delete this checklist?')
    explanation = _('This will also delete all checklist values.')

    return render(request, 'generic/delete.html', locals())


@staff_member_required
def tags(request, type=None):
    if type is None:
        type = Tag.TYPES[0][0]

    title = Checklist._meta.verbose_name_plural
    object_list = Tag.objects.filter(type=type)

    if object_list.count() > 0:
        return redirect(object_list[0].get_admin_url())

    types = Tag.TYPES

    return render(request, 'admin/tags/index.html', locals())


@staff_member_required
def edit_tag(request, type, pk=None):
    if pk is None:
        tag = Tag(type=type)
    else:
        tag = Tag.objects.get(pk=pk)

    TagForm = modelform_factory(Tag, exclude=[])
    form = TagForm(instance=tag)

    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)

        if form.is_valid():
            tag = form.save()
            messages.success(request, _(u'Tag %s saved') % tag.title)
            return redirect(edit_tag, tag.type, tag.pk)

    types = Tag.TYPES
    title = Tag._meta.verbose_name_plural
    object_list = Tag.objects.filter(type=type)
    return render(request, 'admin/tags/form.html', locals())


@staff_member_required
def delete_tag(request, pk):
    tag = Tag.objects.get(pk=pk)

    if request.method == 'POST':
        tag.delete()
        messages.success(request, _('Tag deleted'))
        return redirect(tags, type=tag.type)

    title = _('Really delete this tag?')
    action = str(request.path)

    return render(request, 'generic/delete.html', locals())


@staff_member_required
def settings(request):
    title = _('System Settings')
    ShippingMethodFormset = modelformset_factory(ShippingMethod,
                                                can_delete=True,
                                                extra=0,
                                                exclude=[])
    formset = ShippingMethodFormset(queryset=ShippingMethod.objects.all())

    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)

        if not form.is_valid():
            messages.error(request, _('Check your settings'))
            return render(request, 'admin/settings.html', locals())

        config = form.save()

        if request.POST.get('update_prices'):
            from servo.models import Product
            for p in Product.objects.filter(fixed_price=False):
                p.set_stock_sales_price()
                p.set_exchange_sales_price()
                p.save()

        # formset = ShippingMethodFormset(request.POST)

        # if not formset.is_valid():
        #     messages.error(request, _('Error in shipping method settings'))
        #     return render(request, 'admin/settings.html', locals())

        # formset.save()

        messages.success(request, _('Settings saved'))
        return redirect(settings)

    config = Configuration.conf()
    form = SettingsForm(initial=config)

    return render(request, 'admin/settings.html', locals())


@staff_member_required
def statuses(request):
    object_list = Status.objects.all()
    title = Status._meta.verbose_name_plural
    if object_list.count() > 0:
        return redirect(edit_status, object_list[0].pk)

    return render(request, 'admin/statuses/index.html', locals())


@staff_member_required
def edit_status(request, pk=None):
    if pk is None:
        status = Status()
    else:
        status = Status.objects.get(pk=pk)

    header = _(u'Statuses')
    object_list = Status.objects.all()
    form = StatusForm(instance=status)
    title = Status._meta.verbose_name_plural

    if request.method == 'POST':
        form = StatusForm(request.POST, instance=status)
        if form.is_valid():
            status = form.save()
            messages.success(request, _(u'%s saved') % status.title)
            return redirect(edit_status, status.pk)

    return render(request, 'admin/statuses/form.html', locals())


@staff_member_required
def remove_status(request, pk):
    status = Status.objects.get(pk=pk)
    action = request.path

    if request.method == 'POST':
        status.delete()
        messages.success(request, _(u'%s deleted') % status.title)
        return redirect(statuses)

    return render(request, 'admin/statuses/remove.html', locals())


@staff_member_required
def fields(request, type='customer'):
    data = prep_list_view(Property)
    data['type'] = type
    data['types'] = Property.TYPES
    data['object_list'] = Property.objects.filter(type=type)

    if data['object_list'].count() > 0:
        field = data['object_list'][0]
        return redirect(edit_field, field.type, field.pk)

    return render(request, 'admin/fields/index.html', data)


@staff_member_required
def edit_field(request, type, pk=None):
    if pk is None:
        field = Property(type=type)
    else:
        field = Property.objects.get(pk=pk)

    FieldForm = modelform_factory(Property, exclude=[])

    types = Property.TYPES
    title = Property._meta.verbose_name_plural
    object_list = Property.objects.filter(type=type)
    form = FieldForm(instance=field)

    if request.method == 'POST':
        form = FieldForm(request.POST, instance=field)

        if form.is_valid():
            field = form.save()
            messages.success(request, _(u'Field saved'))
            return redirect(field.get_admin_url())

    return render(request, 'admin/fields/form.html', locals())


@staff_member_required
def delete_field(request, pk=None):
    field = Property.objects.get(pk=pk)

    if request.method == 'POST':
        field.delete()
        messages.success(request, _(u'Field deleted'))
        return redirect(fields, type=field.type)

    data = {'title': _('Really delete this field?')}
    data['action'] = request.path

    return render(request, 'generic/delete.html', data)


@staff_member_required
def list_templates(request):
    object_list = Template.objects.all()
    title = Template._meta.verbose_name_plural
    if object_list.count() > 0:
        return redirect(object_list[0].get_admin_url())
    return render(request, "admin/templates/list_templates.html", locals())


@staff_member_required
def edit_template(request, pk=None):

    if pk is None:
        template = Template()
    else:
        template = Template.objects.get(pk=pk)

    form = TemplateForm(instance=template)

    if request.method == 'POST':
        form = TemplateForm(request.POST, instance=template)

        if form.is_valid():
            template = form.save()
            messages.success(request, _(u'Template %s saved') % template.title)
            # generic view...
            return redirect(template.get_admin_url())

    form = form
    object_list = Template.objects.all()
    title = Template._meta.verbose_name_plural
    return render(request, 'admin/templates/form.html', locals())


@staff_member_required
def delete_template(request, pk):
    template = Template.objects.get(pk=pk)

    if request.method == 'POST':
        template.delete()
        messages.success(request, _(u'Template %s deleted') % template.title)
        return redirect(list_templates)

    title = _('Really delete this template?')
    action = str(request.path)
    return render(request, 'generic/delete.html', locals())


@staff_member_required
def list_users(request):
    object_list = User.objects.filter(is_visible=True)
    title = User._meta.verbose_name_plural
    locations = Location.objects.all()

    if object_list.count() > 0:
        return redirect(object_list[0].get_admin_url())

    return render(request, 'admin/users/index.html', locals())


@staff_member_required
def list_groups(request):
    object_list = Group.objects.all()
    title = _('Users & Groups')

    return render(request, 'admin/users/groups.html', locals())


@staff_member_required
def edit_group(request, pk=None):
    title = _(u'Edit Group')
    object_list = Group.objects.all()

    if pk is None:
        group = Group()
        form = GroupForm(instance=group)
    else:
        group = Group.objects.get(pk=pk)
        title = group.name
        form = GroupForm(instance=group)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, _(u'Group saved'))
            return redirect(list_groups)

    return render(request, 'admin/users/group_form.html', locals())


@staff_member_required
def delete_group(request, pk):
    group = Group.objects.get(pk=pk)

    if request.method == "POST":
        group.delete()
        messages.success(request, _("Group deleted"))
        return redirect(list_groups)

    data = {'action': request.path}

    return render(request, "admin/users/delete_group.html", data)


@staff_member_required
def delete_user(request, user_id):
    user = User.objects.get(pk=user_id)

    if request.method == "POST":
        try:
            user.delete()
            messages.success(request, _("User deleted"))
        except Exception, e:
            messages.error(request, e)

        return redirect(list_users)

    return render(request, "admin/users/remove.html", locals())


@staff_member_required
def delete_user_token(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete_tokens()
    messages.success(request, _('API tokens deleted'))
    return redirect(edit_user, user.pk)


@staff_member_required
def create_user_token(request, user_id):
    user = User.objects.get(pk=user_id)
    token = user.create_token()
    messages.success(request, _('API token created'))
    return redirect(edit_user, user.pk)


@staff_member_required
def edit_user(request, pk=None):
    if pk is None:
        user = User(location=request.user.location)
        user.locale = request.user.locale
        user.region = request.user.region
        user.timezone = request.user.timezone
    else:
        user = get_object_or_404(User, pk=pk)

    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            User.refresh_nomail()
            if request.POST.get('password1'):
                user.set_password(request.POST['password1'])
                user.save()
            messages.success(request, _(u"User %s saved") % user.get_name())
            return redirect(edit_user, user.pk)
        else:
            messages.error(request, _("Error in user profile data"))

    object_list = User.objects.filter(is_visible=True)
    
    if request.GET.get('l'):
        object_list = object_list.filter(locations__pk=request.GET['l'])

    title = User._meta.verbose_name_plural
    locations = Location.objects.all()

    if len(object_list) > 0:
        header = _(u'%d users') % len(object_list)

    return render(request, "admin/users/form.html", locals())


@staff_member_required
def locations(request):
    object_list = Location.objects.all()
    title = Location._meta.verbose_name_plural

    if object_list.count() > 0:
        return redirect(object_list[0].get_admin_url())

    return render(request, 'admin/locations/index.html', locals())


@staff_member_required
def edit_location(request, pk=None):
    header = _('Locations')
    object_list = Location.objects.all()
    title = Location._meta.verbose_name_plural

    if pk is None:
        location = Location()
        location.timezone = request.user.timezone
    else:
        location = Location.objects.get(pk=pk)

    form = LocationForm(instance=location)

    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES, instance=location)
        if form.is_valid():
            try:
                location = form.save()
                messages.success(request, _(u'Location %s saved') % location.title)
                return redirect(location.get_admin_url())
            except Exception:
                pass # just show the form with the error

    return render(request, 'admin/locations/form.html', locals())


@staff_member_required
def delete_location(request, pk):
    location = Location.objects.get(pk=pk)

    if request.method == 'POST':
        try:
            location.delete()
            messages.success(request, _(u'%s deleted') % location.title)
        except Exception, e:
            messages.error(request, e)

        return redirect(locations)

    title = _(u'Really delete this location?')
    explanation = _(u'This will not delete the orders at this location')
    action = request.path

    return render(request, 'generic/delete.html', locals())


@staff_member_required
def queues(request):
    data = prep_list_view(Queue)
    if data['object_list'].count() > 0:
        return redirect(data['object_list'][0].get_admin_url())
    data['subtitle'] = _('Create, edit and delete service queues')
    return render(request, 'admin/queues/index.html', data)


@staff_member_required
def edit_queue(request, pk=None):

    StatusFormSet = inlineformset_factory(Queue, QueueStatus, extra=1, exclude=[])

    if pk is None:
        queue = Queue()
        locations = request.user.locations.all()
        form = QueueForm(initial={'locations': locations})
    else:
        queue = Queue.objects.get(pk=pk)
        form = QueueForm(instance=queue, initial={'users': queue.user_set.all()})

    title = _(u'Queues')
    object_list = Queue.objects.all()
    formset = StatusFormSet(instance=queue)

    if request.method == 'POST':
        form = QueueForm(request.POST, request.FILES, instance=queue)

        if form.is_valid():
            try:
                queue = form.save()
                queue.user_set = form.cleaned_data['users']
                queue.save()
            except Exception as e:
                messages.error(request, _('Failed to save queue'))
                return render(request, 'admin/queues/form.html', locals())

            formset = StatusFormSet(request.POST, instance=queue)

            if formset.is_valid():
                formset.save()
                messages.success(request, _(u'%s queue saved') % queue.title)
                return redirect(queue.get_admin_url())
            else:
                messages.error(request, formset.errors)
        else:
            messages.error(request, form.errors)

    return render(request, 'admin/queues/form.html', locals())


@staff_member_required
def delete_queue(request, pk=None):
    queue = Queue.objects.get(pk=pk)

    if request.method == 'POST':
        try:
            queue.delete()
            messages.success(request, _("Queue deleted"))
        except Queue.ProtectedError:
            messages.error(request, _("Cannot delete queue"))

        return redirect(queues)

    return render(request, 'admin/queues/remove.html', locals())


@staff_member_required
def notifications(request):
    data = {'title': _(u'Notifications')}
    return render(request, 'admin/notifications/index.html', data)


@staff_member_required
def edit_notification(request, nid):
    return render(request, 'admin/notifications/form.html')


def list_sites(request):
    if not request.user.is_superuser:
        messages.error(request, _(u"Access denied"))
        return redirect('/login/')

    data = {'sites': Site.objects.all()}
    data['title'] = _(u"Manage Sites")

    return render(request, "admin/sites/index.html", data)


def edit_site(request, pk=None):
    if not request.user.is_superuser:
        messages.add_message(request, messages.ERROR, _(u"Access denied"))
        return redirect('/login/')

    site = Site()
    data = {'title': _(u"New Site")}

    if pk is not None:
        site = Site.objects.get(pk=pk)
        data['title'] = site.name

    SiteForm = modelform_factory(Site, exclude=[])
    form = SiteForm(instance=site)

    if request.method == "POST":

        form = SiteForm(request.POST, instance=site)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, _(u"Site saved"))
            return redirect(list_sites)

    data['form'] = form
    data['sites'] = Site.objects.all()

    return render(request, "admin/sites/edit_site.html", data)


def upload_users(request):
    """
    """
    action = request.path
    form = UserUploadForm()
    title = _('Upload Users')

    if request.method == 'POST':
        form = UserUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                users = form.save()
                messages.success(request, _('%d users imported') % len(users))
            except Exception, e:
                messages.error(request, e)
        else:
            messages.error(request, form.errors)

        return redirect(list_users)

    return render(request, "admin/users/upload_users.html", locals())


class Backup(object):
    @classmethod
    def all(cls):
        from glob import glob
        return [cls(s) for s in glob("backups/*.gz")]

    def __init__(self, path):
        import os
        self.path = path
        self.filename = os.path.basename(path)
        self.filesize = os.path.getsize(path)

    def get_wrapper(self):
        from django.core.servers.basehttp import FileWrapper
        return FileWrapper(file(self.path))

    def get_response(self):
        from django.http import HttpResponse
        wrapper = self.get_wrapper()
        response = HttpResponse(wrapper, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % self.filename
        response['Content-Length'] = self.filesize
        return response

def backups(request):

    if request.GET.get('dl'):
        backup = Backup("backups/%s" % request.GET['dl'])
        return backup.get_response()

    title = _('Backups')
    backups = Backup.all()
    return render(request, "admin/backups.html", locals())
