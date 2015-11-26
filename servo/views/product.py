# -*- coding: utf-8 -*-

from decimal import *

from django.db.models import Q
from django.db import IntegrityError

from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, get_object_or_404

from servo.lib.utils import paginate, send_csv
from servo.models import (Attachment, TaggedItem,
                          Product, ProductCategory,
                          Inventory, Location, inventory_totals,
                          GsxAccount,)
from servo.forms.product import ProductForm, CategoryForm, ProductSearchForm


def prep_list_view(request, group='all'):
    """
    Prepares the product list view
    """
    title = _("Products")
    search_hint = "products"
    all_products = Product.objects.all()
    categories = ProductCategory.objects.all()

    if group == 'all':
        group = ProductCategory(title=_('All'), slug='all')
    elif group == 'None':
        group = ProductCategory(title=_('None'), slug='none')
        all_products = all_products.filter(categories=None)
    else:
        group = categories.get(slug=group)
        all_products = group.get_products()

    if request.method == 'POST':
        form = ProductSearchForm(request.POST)
        if form.is_valid():
            fdata = form.cleaned_data

            description = fdata.get('description')
            if description:
                all_products = all_products.filter(description__icontains=description)

            title = fdata.get('title')
            if title:
                all_products = all_products.filter(title__icontains=title)

            code = fdata.get('code')
            if code:
                all_products = all_products.filter(code__icontains=code)

            tag = fdata.get('tag')
            if tag:
                tag = tag.tag
                title += u" / %s" % tag
                all_products = all_products.filter(tags__tag=tag)

            location = fdata.get('location')
            if location:
                all_products = all_products.filter(inventory__location=location)
    else:
        form = ProductSearchForm()

    title += u" / %s" % group.title
    page = request.GET.get("page")
    products = paginate(all_products.distinct(), page, 25)

    return locals()


def tags(request):
    """
    Returns all product tags
    """
    from servo.lib.utils import json_response
    tags = TaggedItem.objects.filter(content_type__model="product")
    tags = tags.distinct("tag").values_list("tag", flat=True)
    return json_response(list(tags))


def list_products(request, group='all'):
    data = prep_list_view(request, group)
    p, s = inventory_totals()
    data['total_sales_value'] = s
    data['total_purchase_value'] = p

    return render(request, "products/index.html", data)


@permission_required("servo.change_product")
def upload_gsx_parts(request, group=None):
    from servo.forms.product import PartsImportForm
    form = PartsImportForm()

    data = {'action': request.path}

    if request.method == "POST":

        form = PartsImportForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.cleaned_data
            filename = "servo/uploads/products/partsdb.csv"
            destination = open(filename, "wb+")

            for chunk in data['partsdb'].chunks():
                destination.write(chunk)

            messages.success(request, _("Parts database uploaded for processing"))
            return redirect(list_products)

    data['form'] = form
    return render(request, "products/upload_gsx_parts.html", data)


@permission_required("servo.change_product")
def get_inventory_report(request):
    """
    Returns stocked amount of products at each location
    """
    import re
    from django.db import connection
    cursor = connection.cursor()
    location_map = {}

    for l in Location.objects.filter(enabled=True):
         location_map[str(l.pk)] = l.title

    # @TODO this should be rewritten as a pivot query
    # but this will have to do for now. This is still much
    # faster than using the ORM.
    query = """SELECT p.id, p.code, l.id, i.amount_stocked 
    FROM servo_product p, servo_inventory i, servo_location l
        WHERE p.id = i.product_id AND l.id = i.location_id
        ORDER BY p.id ASC"""
    cursor.execute(query)

    response = HttpResponse(content_type="text/plain; charset=utf-8")
    filename = 'servo_inventory_report.txt'
    #response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    header = ['ID', 'CODE'] + location_map.values()
    response.write("\t".join(header) + "\n")
    inventory, codemap = {}, {}

    for k in cursor.fetchall():
        product_id = unicode(k[0])
        codemap[product_id] = k[1] # map product IDs to product codes
        inv_slot = {k[2]: k[3]}

        try:
            inventory[product_id].append(inv_slot)
        except KeyError:
            inventory[product_id] = [inv_slot]

    for k, v in inventory.iteritems():
        inventory_cols = []
        for i, x in location_map.iteritems():
            for p in v:
                amount = p.get(i, '0') # fill empty inventory slots with zeros
                inventory_cols.append(amount)

        code = unicode(codemap[k])
        row = [k, code] + inventory_cols
        response.write("\t".join(row) + "\n")

    return response


@permission_required("servo.change_product")
def download_products(request, group="all"):
    """
    Downloads entire product DB or just ones belonging to a group
    """
    filename = "products"
    data = u"ID\tCODE\tTITLE\tPURCHASE_PRICE\tSALES_PRICE\tSTOCKED\n"

    if group == "all":
        products = Product.objects.all()
    else:
        category = get_object_or_404(ProductCategory, slug=group)
        products = category.get_products()
        filename = group

    # @FIXME: Add total stocked amount to product
    # currently the last column is a placeholder for stock counts in inventory uploads
    for p in products:
        row = [unicode(i) for i in (p.pk, p.code, p.title, 
                                    p.price_purchase_stock,
                                    p.price_sales_stock, 0)]
        data += "\t".join(row) + "\n"

    return send_csv(data, filename)


@permission_required("servo.change_product")
def upload_products(request, group=None):
    """"
    Format should be the same as from download_products
    """
    import io
    from servo.forms import ProductUploadForm
    location = request.user.get_location()
    form = ProductUploadForm()

    if request.method == "POST":
        form = ProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            string = u''
            category = form.cleaned_data['category']
            data = form.cleaned_data['datafile'].read()

            for i in ('utf-8', 'latin-1',):
                try:
                    string = data.decode(i)
                except:
                    pass

            if not string:
                raise ValueError(_('Unsupported file encoding'))

            i = 0
            sio = io.StringIO(string, newline=None)

            for l in sio.readlines():
                cols = l.strip().split("\t")

                if cols[0] == "ID":
                    continue # Skip header row

                if len(cols) < 2:
                    continue # Skip empty rows

                if len(cols) < 6:  # No ID row, pad it
                    cols.insert(0, "")

                product, created = Product.objects.get_or_create(code=cols[1])

                # Remove Excel escapes
                product.title = cols[2].strip(' "').replace('""', '"')
                product.price_purchase_stock = cols[3].replace(',', '.')
                product.price_sales_stock = cols[4].replace(',', '.')
                product.save()

                if category:
                    product.categories.add(category)

                inventory, created = Inventory.objects.get_or_create(
                    product=product, location=location
                )
                inventory.amount_stocked = cols[5]
                inventory.save()
                i += 1

            messages.success(request, _(u"%d products imported") % i)

            return redirect(list_products)

    action = request.path
    title = _("Upload products")
    return render(request, "products/upload_products.html", locals())


@permission_required("servo.change_product")
def edit_product(request, pk=None, code=None, group='all'):
    """
    Edits a Product! :-)
    """
    initial = {}
    product = Product()

    data = prep_list_view(request, group)

    if pk is not None:
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)

    if not group == 'all':
        cat = get_object_or_404(ProductCategory, slug=group)
        initial = {'categories': [cat]}
        data['group'] = cat

    product.update_photo()

    if code is not None:
        product = cache.get(code)

    form = ProductForm(instance=product, initial=initial)
    InventoryFormset = inlineformset_factory(Product,
                                             Inventory,
                                             extra=1,
                                             max_num=1,
                                             exclude=[])

    formset = InventoryFormset(
        instance=product,
        initial=[{'location': request.user.location}]
    )

    if request.method == "POST":

        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():

            product = form.save()
            content_type = ContentType.objects.get(model="product")

            for a in request.POST.getlist("attachments"):
                doc = Attachment.objects.get(pk=a)
                product.attachments.add(doc)

            tags = [x for x in request.POST.getlist('tag') if x != '']

            for t in tags:
                tag, created = TaggedItem.objects.get_or_create(
                    content_type=content_type,
                    object_id=product.pk,
                    tag=t)
                tag.save()

            formset = InventoryFormset(request.POST, instance=product)

            if formset.is_valid():
                formset.save()
                messages.success(request, _(u"Product %s saved") % product.code)
                return redirect(product)
            else:
                messages.error(request, _('Error in inventory details'))
        else:
            messages.error(request, _('Error in product info'))

    data['form'] = form
    data['product'] = product
    data['formset'] = formset
    data['title'] = product.title

    return render(request, "products/form.html", data)


@permission_required("servo.delete_product")
def delete_product(request, pk, group):
    from django.db.models import ProtectedError
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        try:
            product.delete()
            Inventory.objects.filter(product=product).delete()
            messages.success(request, _("Product deleted"))
        except ProtectedError:
            messages.error(request, _('Cannot delete product'))

        return redirect(list_products, group)

    action = request.path
    return render(request, 'products/remove.html', locals())


def view_product(request, pk=None, code=None, group=None):

    product = Product()
    inventory = Inventory.objects.none()

    try:
        product = get_object_or_404(Product, pk=pk)
        inventory = Inventory.objects.filter(product=product)
    except Product.DoesNotExist:
        product = cache.get(code)

    data = prep_list_view(request, group)

    data['product'] = product
    data['inventory'] = inventory
    data['title'] = '%s - %s' % (product.code, product.title)

    # Collect data for Sales/Purchases/Invoices tabs
    results_per_page = 50
    page = request.GET.get('page')

    sales = product.serviceorderitem_set.all().select_related('order')
    sales = sales.order_by('-id')
    data['sales'] = paginate(sales, page, results_per_page)

    purchases = product.purchaseorderitem_set.all().select_related('purchase_order')
    purchases = purchases.order_by('-id')
    data['purchases'] = paginate(purchases, page, results_per_page)

    invoices = product.invoiceitem_set.all().select_related('invoice')
    invoices = invoices.order_by('-id')
    data['invoices'] = paginate(invoices, page, results_per_page)

    return render(request, "products/view.html", data)


@permission_required("servo.change_productcategory")
def edit_category(request, slug=None, parent_slug=None):

    form = CategoryForm()
    category = ProductCategory()

    if slug is not None:
        category = get_object_or_404(ProductCategory, slug=slug)
        form = CategoryForm(instance=category)

    if parent_slug is not None:
        parent = get_object_or_404(ProductCategory, slug=parent_slug)
        form = CategoryForm(initial={'parent': parent.pk})

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                category = form.save()
            except IntegrityError:
                error = _(u'Category %s already exists') % category.title
                messages.error(request, error)
                return redirect(list_products)
            messages.success(request, _(u"Category %s saved") % category.title)
            return redirect(category)
        else:
            messages.error(request, form.errors)
            return redirect(list_products)

    return render(request, "products/category_form.html", locals())


@permission_required("servo.delete_productcategory")
def delete_category(request, slug):

    category = get_object_or_404(ProductCategory, slug=slug)

    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category deleted"))
        return redirect(list_products)

    data = {'category': category}
    data['action'] = request.path
    return render(request, 'products/delete_category.html', data)


@permission_required("servo.change_order")
def choose_product(request, order_id, product_id=None, target_url="orders-add_product"):
    """
    order_id can be either Service Order or Purchase Order
    """
    data = {'order': order_id}
    data['action'] = request.path
    data['target_url'] = target_url

    if request.method == "POST":
        query = request.POST.get('q')

        if len(query) > 2:
            products = Product.objects.filter(
                Q(code__icontains=query) | Q(title__icontains=query)
            )
            data['products'] = products

        return render(request, 'products/choose-list.html', data)

    return render(request, 'products/choose.html', data)


def get_info(request, location, code):
    try:
        product = Product.objects.get(code=code)
        inventory = Inventory.objects.filter(product=product)
    except Product.DoesNotExist:
        product = cache.get(code)

    return render(request, 'products/get_info.html', locals())


def update_price(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        GsxAccount.default(request.user)
        product.update_price()
        messages.success(request, _('Price info updated from GSX'))
    except Exception as e:
        messages.error(request, _('Failed to update price from GSX'))

    return redirect(product)
