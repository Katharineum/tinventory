#  Copyright (c) 2019 Jonathan Weth, Lübeck.
#
#  This file is part of TInventory.
#
#  TInventory is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License.
#
#  TInventory is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TInventory.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.http import FileResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.utils import timezone

from api.models import Category, Location, Preset, Item, Person, CheckOutProcess, Check
from api.reports import barcode_pdf, loan_form_pdf, check_in_confirmation_pdf
from ui.forms import CategoryForm, LocationForm, PresetForm, ItemForm, InventoryForm, PersonForm


@login_required
def index(request):
    context = {
        "count_items": Item.objects.all().count(),
        "count_presets": Preset.objects.all().count(),

    }
    available = 0
    checked_out = 0
    not_in_time = 0
    for item in Item.objects.all():
        if item.is_available():
            available += 1
        else:
            checked_out += 1
            check = item.checks.filter(checked_in=False)[0]
            if not check.check_out.is_in_time():
                not_in_time += 1
    context["count_available_items"] = available
    context["count_checked_out_items"] = checked_out
    context["count_not_in_time"] = not_in_time

    return render(request, "ui/index.html", context=context)


@login_required
@permission_required("api.view_category")
def categories(request):
    categories = Category.objects.all()
    context = {
        "categories": categories
    }
    if request.session.get("msg", False):
        context["msg"] = request.session["msg"]
        request.session["msg"] = None

    return render(request, "ui/categories.html", context)


@login_required
@permission_required("api.change_category")
def category_edit(request, id):
    category = get_object_or_404(Category, pk=id)

    if request.method == 'GET':
        form = CategoryForm(instance=category)
    else:
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            # name = form.cleaned_data['name']
            # Category.objects.filter(id=id).update(name=name)
            form.save()
            request.session["msg"] = "Die Kategorie wurde erfolgreich aktualisiert."
            return redirect('ui_categories')

    return render(request, "ui/category_form.html", {"category": category, "form": form, "mode": "edit"})


@login_required
@permission_required("api.add_category")
def category_new(request):
    if request.method == 'GET':
        form = CategoryForm()
    else:
        form = CategoryForm(request.POST)
        if form.is_valid():
            # name = form.cleaned_data['name']
            # Category.objects.create(name=name)
            form.save()
            request.session["msg"] = "Die Kategorie wurde erfolgreich erstellt."
            return redirect('ui_categories')

    return render(request, "ui/category_form.html", {"form": form, "mode": "new"})


@login_required
@permission_required("api.delete_category")
def category_delete(request, id):
    category = get_object_or_404(Category, pk=id)
    category.delete()
    request.session["msg"] = "Die Kategorie wurde erfolgreich gelöscht."
    return redirect("ui_categories")


#############
# LOCATIONS #
#############

location_decorators = [login_required, permission_required("api.change_location")]


@login_required
@permission_required("api.view_location")
def locations(request):
    locations = Location.objects.all()
    context = {
        "locations": locations
    }
    if request.session.get("msg", False):
        context["msg"] = request.session["msg"]
        request.session["msg"] = None

    return render(request, "ui/locations.html", context)


@login_required
@permission_required("api.change_location")
def location_edit(request, id):
    location = get_object_or_404(Location, pk=id)

    if request.method == 'GET':
        form = LocationForm(instance=location)
    else:
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            request.session["msg"] = "Der Ort wurde erfolgreich aktualisiert."
            return redirect('ui_locations')

    return render(request, "ui/location_form.html", {"location": location, "form": form, "mode": "edit"})


@method_decorator(location_decorators, name='get')
class LocationDetailView(DetailView):
    model = Location
    template_name = "ui/location_detail.html"


@login_required
@permission_required("api.change_item")
def location_add_item(request, pk):
    if request.method == "GET":
        if "item_id" in request.GET.keys():
            try:
                item_id = int(request.GET["item_id"])

                location = Location.objects.get(pk=pk)
                item = Item.objects.get(pk=item_id)

                item.location = location

                item.save()
                location.save()

                status = 200
                data = {"status": "Success"}

            except ValueError:
                status, data = give_location_error(400, "item_id is not an integer")  # 400 - bad request
        else:
            status, data = give_location_error(400, "item_id isn set")  # 400 - bad request
    else:
        status, data = give_location_error(405, "request method has to be GET")  # 405 - method not allowed
    return JsonResponse(data=data, status=status)


def give_location_error(code: int, msg=""):
    status = code
    data = {
        "status": "Error",
        "error_code": code,
    }
    if msg:
        data["message"] = msg

    return status, data


@login_required
@permission_required("api.add_location")
def location_new(request):
    if request.method == 'GET':
        form = LocationForm()
    else:
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            request.session["msg"] = "Der Ort wurde erfolgreich erstellt."
            return redirect('ui_locations')

    return render(request, "ui/location_form.html", {"form": form, "mode": "new"})


@login_required
@permission_required("api.delete_location")
def location_delete(request, id):
    location = get_object_or_404(Location, pk=id)
    location.delete()
    request.session["msg"] = "Der Ort wurde erfolgreich gelöscht."
    return redirect("ui_locations")


@login_required
@permission_required("api.view_preset")
def presets(request):
    presets = Preset.objects.all()
    context = {
        "presets": presets
    }
    if request.session.get("msg", False):
        context["msg"] = request.session["msg"]
        request.session["msg"] = None

    return render(request, "ui/presets.html", context)


@login_required
@permission_required("api.view_preset")
def preset_view(request, id):
    preset = get_object_or_404(Preset, pk=id)
    context = {
        "preset": preset
    }
    return render(request, "ui/preset_view.html", context)


@login_required
@permission_required("api.change_preset")
def preset_edit(request, id):
    preset = get_object_or_404(Preset, pk=id)

    if request.method == 'GET':
        form = PresetForm(instance=preset)
    else:
        form = PresetForm(request.POST, request.FILES, instance=preset)
        if form.is_valid():
            form.save()
            request.session["msg"] = "Das Preset wurde erfolgreich aktualisiert."
            return redirect('ui_presets')

    return render(request, "ui/preset_form.html", {"preset": preset, "form": form, "mode": "edit"})


@login_required
@permission_required("api.add_preset")
def preset_new(request):
    if request.method == 'GET':
        form = PresetForm()
    else:
        form = PresetForm(request.POST)
        if form.is_valid():
            form.save()
            request.session["msg"] = "Das Preset wurde erfolgreich erstellt."
            return redirect('ui_presets')

    return render(request, "ui/preset_form.html", {"form": form, "mode": "new"})


@login_required
@permission_required("api.delete_preset")
def preset_delete(request, id):
    preset = get_object_or_404(Preset, pk=id)
    preset.delete()
    request.session["msg"] = "Das Preset wurde erfolgreich gelöscht."
    return redirect("ui_presets")


@login_required
@permission_required("api.view_item")
def items(request):
    items = Item.objects.all()
    context = {
        "items": items
    }
    if request.session.get("msg", False):
        context["msg"] = request.session["msg"]
        request.session["msg"] = None

    return render(request, "ui/items.html", context)


@login_required
@permission_required("api.view_item")
def item_view(request, id):
    item = get_object_or_404(Item, pk=id)
    context = {
        "item": item
    }
    return render(request, "ui/item_view.html", context)


@login_required
@permission_required("api.change_item")
def item_edit(request, id):
    item = get_object_or_404(Item, pk=id)

    if request.method == 'GET':
        form = ItemForm(instance=item)
    else:
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            request.session["msg"] = "Das Objekt wurde erfolgreich aktualisiert."
            return redirect('ui_items')

    return render(request, "ui/item_form.html", {"item": item, "form": form, "mode": "edit"})


@login_required
@permission_required("api.add_item")
def item_new(request):
    if request.method == 'GET':
        form = ItemForm()
    else:
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            request.session["msg"] = "Das Objekt wurde erfolgreich erstellt."
            return redirect('ui_items')

    return render(request, "ui/item_form.html", {"form": form, "mode": "new"})


@login_required
@permission_required("api.delete_item")
def item_delete(request, id):
    item = get_object_or_404(Item, pk=id)
    item.delete()
    request.session["msg"] = "Das Objekt wurde erfolgreich gelöscht."
    return redirect("ui_items")


@login_required
@permission_required("api.view_item")
def item_barcode(request, id):
    item = get_object_or_404(Item, pk=id)
    filename = barcode_pdf(item)
    f = open(filename, "rb")
    return FileResponse(f, content_type="application/pdf")


@login_required
@permission_required("api.add_item")
def inventory(request):
    context = {}
    if request.method == 'GET':
        form = InventoryForm()
    else:
        form = InventoryForm(request.POST)
        if form.is_valid():
            item = form.save()
            context["msg"] = "Das Objekt wurde erfolgreich erstellt."
            context["created_item"] = item
            initial = {}
            initial["category_select"] = item.category
            initial["preset_select"] = item.preset
            initial["location"] = item.location
            form = InventoryForm(initial=initial)
    context["form"] = form
    return render(request, "ui/inventory.html", context)


@login_required
@permission_required("api.view_person")
def persons(request):
    persons = Person.objects.all()
    context = {
        "persons": persons
    }
    if request.session.get("msg", False):
        context["msg"] = request.session["msg"]
        request.session["msg"] = None

    return render(request, "ui/persons.html", context)


@login_required
@permission_required("api.view_person")
def person_view(request, id):
    person = get_object_or_404(Person, pk=id)
    context = {
        "person": person
    }
    return render(request, "ui/person_view.html", context)


@login_required
@permission_required("api.change_person")
def person_edit(request, id):
    person = get_object_or_404(Person, pk=id)

    if request.method == 'GET':
        form = PersonForm(instance=person)
    else:
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            request.session["msg"] = "Die Person wurde erfolgreich aktualisiert."
            return redirect('ui_persons')

    return render(request, "ui/person_form.html", {"person": person, "form": form, "mode": "edit"})


@login_required
@permission_required("api.add_person")
def person_new(request):
    if request.method == 'GET':
        form = PersonForm()
    else:
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            request.session["msg"] = "Die Person wurde erfolgreich erstellt."
            return redirect('ui_persons')

    return render(request, "ui/person_form.html", {"form": form, "mode": "new"})


@login_required
@permission_required("api.delete_person")
def person_delete(request, id):
    person = get_object_or_404(Person, pk=id)
    person.delete()
    request.session["msg"] = "Die Person wurde erfolgreich gelöscht."
    return redirect("ui_persons")


@login_required
@permission_required("api.check_out")
def check_out(request):
    msg = False
    msg_type = "success"
    step = request.session["step"] if request.session.get("step", False) else 1
    if step > 1:
        process = CheckOutProcess.objects.get(id=request.session["process"])

    if request.method == "POST":

        # Cancel checkout
        if request.POST.get("cancel", False):
            # Delete process object
            if step > 1:
                process.delete()

            # Delete session vars
            del request.session["step"]
            del request.session["process"]

            # Redirect to base url
            return redirect("ui_check_out")

        if step == 1 and request.POST.get("select-person", False):
            # Select person
            try:
                person = Person.objects.get(id=int(request.POST["select-person"]))
            except (Person.DoesNotExist, ValueError):
                return redirect("ui_check_out")
            process = CheckOutProcess.objects.create(borrowing_person=person, lending_user=request.user)
            request.session["process"] = process.id
            request.session["step"] = 2
            step = 2

        if (step == 2 or step == 3) and request.POST.get("delete", False):
            if step == 3 and process.checks.count() < 2:
                return redirect("ui_check_out")
            try:
                id = int(request.POST["delete"])
                check = process.checks.get(id=id)
                check.delete()
                msg = "Das Objekt wurde erfolgreich von der Check-Out-Liste entfernt."
            except (Check.DoesNotExist, ValueError):
                return redirect("ui_check_out")

        if step == 2 and request.POST.get("scan", False):
            scan = request.POST["scan"]
            item = None

            try:
                id = int(scan)
                item = Item.objects.get(id=id)
            except (Item.DoesNotExist, ValueError):
                try:
                    item = Item.objects.get(barcode=scan)
                except Item.DoesNotExist:
                    msg = "Es gibt kein Objekt mit dieser ID oder diesem Barcode: {}".format(scan)
                    msg_type = "bad"

            if msg_type == "success":
                if not item.is_available():
                    if item.checks.all()[0].check_out == process:
                        msg = "Dieses Objekt ist bereits zur Check-Out-Liste hinzugefügt worden."
                        msg_type = "bad"
                    else:
                        msg = "Dieses Objekt ist aktuell ausgecheckt. Bitte vor dem Check-Out wieder Einchecken."
                        msg_type = "bad"
            if msg_type == "success":
                check = process.checks.create(item=item)
                msg = "Das Objekt wurde erfolgreich zur Check-Out-Liste hinzugefügt."

        if step == 2 and request.POST.get("confirm", False) and process.checks.count() > 0:
            request.session["step"] = 3
            step = 3

        elif step == 3 and request.POST.get("confirm", False) and process.checks.count() > 0:
            process.is_check_out_in_process = False
            process.checked_out_at = timezone.now()
            process.save()
            del request.session["step"]
            del request.session["process"]
            step = 4

    if step == 1:
        technicians = Person.objects.all().filter(is_technician=True).order_by("name")
        persons = Person.objects.all().filter(is_technician=False).order_by("name")
        return render(request, "ui/check-out-1.html", context={"technicians": technicians, "persons": persons})
    elif step == 2:
        return render(request, "ui/check-out-2.html", context={"process": process, "msg": msg, "msg_type": msg_type})
    elif step == 3:
        return render(request, "ui/check-out-3.html", context={"process": process})
    elif step == 4:
        return render(request, "ui/check-out-done.html", context={"process": process})


@login_required
@permission_required("api.check_out")
def loan_form(request, id):
    process = get_object_or_404(CheckOutProcess, pk=id)
    filename = loan_form_pdf(process)
    f = open(filename, "rb")
    return FileResponse(f, content_type="application/pdf")


@login_required
@permission_required("api.check_out")
def checks(request):
    checks = CheckOutProcess.objects.all().filter(is_check_out_in_process=False)
    context = {
        "checks": checks
    }
    if request.session.get("msg", False):
        context["msg"] = request.session["msg"]
        request.session["msg"] = None

    return render(request, "ui/checks.html", context)


@login_required
@permission_required("api.check_out")
def check_view(request, id):
    check = get_object_or_404(CheckOutProcess, pk=id, is_check_out_in_process=False)
    context = {
        "check": check
    }
    return render(request, "ui/check_view.html", context)


@login_required
@permission_required("api.check_out")
def check_continue(request, id):
    process = get_object_or_404(CheckOutProcess, pk=id)
    request.session["process"] = process.id
    request.session["step"] = 2
    return redirect("ui_check_out")


@login_required
@permission_required("api.check_in")
def check_in(request):
    context = {}
    msg = False
    if request.method == "POST" and request.POST.get("scan", False):
        scan = request.POST["scan"]
        check = None

        try:
            id = int(scan)
            check = Check.objects.get(item_id=id, checked_in=False)
        except (Check.DoesNotExist, ValueError):
            try:
                check = Check.objects.get(item__barcode=scan, checked_in=False)
            except Check.DoesNotExist:
                msg = "not_found"

        if not msg:
            check.checked_in = True
            check.checked_in_at = timezone.now()
            check.checked_in_by = request.user
            check.save()
            context["check"] = check
            msg = "checked_in"

    context["msg"] = msg
    return render(request, "ui/check-in.html", context)


@login_required
@permission_required("api.check_in")
def check_in_confirmation(request, id):
    process = get_object_or_404(CheckOutProcess, pk=id)
    filename = check_in_confirmation_pdf(process)
    f = open(filename, "rb")
    return FileResponse(f, content_type="application/pdf")


def license(request):
    LICENSE_APACHE_2 = "Apache 2.0 License"
    LICENSE_BSD = "2-Clause BSD License"
    LICENSE_BSD_3 = "3-Clause BSD License"
    LICENSE_MIT = "MIT License"

    components = [
        ("Docker (u.a. Engine, CLI, docker-compose)", "https://github.com/docker", LICENSE_APACHE_2,
         "https://github.com/docker/docker/blob/master/LICENSE"),
        ("Django", "https://www.djangoproject.com/", "Django BSD License",
         "https://github.com/django/django/blob/master/LICENSE"),
        ("Python 3", "https://www.python.org/", "PSF LICENSE AGREEMENT FOR PYTHON",
         "https://docs.python.org/3/license.html"),
        (
            "Bootstrap", "https://getbootstrap.com/", LICENSE_MIT,
            "https://github.com/twbs/bootstrap/blob/master/LICENSE"),
        ("jQuery", "https://jquery.com/", LICENSE_MIT, "https://github.com/jquery/jquery/blob/master/LICENSE.txt"),
        ("FontAwesome Icon Font", "https://github.com/FortAwesome/Font-Awesome", "SIL OFL 1.1 License",
         "https://scripts.sil.org/OFL"),
        ("DataTables", "https://datatables.net", LICENSE_MIT, "https://datatables.net/license/mit"),
        ("pip", "https://pypi.org/project/pip/", LICENSE_MIT, "https://github.com/pypa/pip/blob/master/LICENSE.txt"),
        ("requests", "https://requests.kennethreitz.org/", LICENSE_APACHE_2,
         "https://github.com/psf/requests/blob/master/LICENSE"),
        ("django-bootstrap-form", "https://github.com/tzangms/django-bootstrap-form", LICENSE_BSD_3,
         "https://github.com/tzangms/django-bootstrap-form/blob/master/LICENSE"),
        ("django-cors-headers", "https://github.com/adamchainz/django-cors-headers", LICENSE_MIT,
         "https://github.com/adamchainz/django-cors-headers/blob/master/LICENSE"),
        ("django-oauth-toolkit", "https://github.com/jazzband/django-oauth-toolkit", LICENSE_BSD,
         "https://github.com/jazzband/django-oauth-toolkit/blob/master/LICENSE"),
        ("django-widget-tweaks", "https://github.com/jazzband/django-widget-tweaks", LICENSE_MIT,
         "https://github.com/jazzband/django-widget-tweaks/blob/master/LICENSE"),
        ("djangorestframework", "https://www.django-rest-framework.org/", LICENSE_BSD_3,
         "https://www.django-rest-framework.org/#license"),
        ("fpdf (PyFPDF)", "https://github.com/reingart/pyfpdf", "GNU Lesser General Public License v3.0",
         "https://github.com/reingart/pyfpdf/blob/master/LICENSE"),

    ]
    components.sort(key=lambda elem: elem[0].lower())
    return render(request, "ui/license.html", context={"components": components})
