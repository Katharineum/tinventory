from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.utils import timezone

from api.models import Category, Location, Preset, Item, Person, CheckOutProcess, Check
from api.reports import barcode_pdf, loan_form_pdf, check_in_confirmation_pdf
from ui.forms import CategoryForm, LocationForm, PresetForm, ItemForm, InventoryForm, PersonForm


@login_required
def index(request):
    return render(request, "ui/index.html")


@login_required
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
def category_delete(request, id):
    category = get_object_or_404(Category, pk=id)
    category.delete()
    request.session["msg"] = "Die Kategorie wurde erfolgreich gelöscht."
    return redirect("ui_categories")


@login_required
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
def location_edit(request, id):
    location = get_object_or_404(Location, pk=id)

    if request.method == 'GET':
        form = LocationForm(instance=location)
    else:
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            # name = form.cleaned_data['name']
            # number = form.cleaned_data["number"]
            # Location.objects.filter(id=id).update(name=name, number=number)
            request.session["msg"] = "Der Ort wurde erfolgreich aktualisiert."
            return redirect('ui_locations')

    return render(request, "ui/location_form.html", {"location": location, "form": form, "mode": "edit"})


@login_required
def location_new(request):
    if request.method == 'GET':
        form = LocationForm()
    else:
        form = LocationForm(request.POST)
        if form.is_valid():
            # name = form.cleaned_data['name']
            # number = form.cleaned_data["number"]
            # Location.objects.create(name=name, number=number)
            form.save()
            request.session["msg"] = "Der Ort wurde erfolgreich erstellt."
            return redirect('ui_locations')

    return render(request, "ui/location_form.html", {"form": form, "mode": "new"})


@login_required
def location_delete(request, id):
    location = get_object_or_404(Location, pk=id)
    location.delete()
    request.session["msg"] = "Der Ort wurde erfolgreich gelöscht."
    return redirect("ui_locations")


@login_required
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
def preset_view(request, id):
    preset = get_object_or_404(Preset, pk=id)
    context = {
        "preset": preset
    }
    return render(request, "ui/preset_view.html", context)


@login_required
def preset_edit(request, id):
    preset = get_object_or_404(Preset, pk=id)

    if request.method == 'GET':
        form = PresetForm(instance=preset)
    else:
        form = PresetForm(request.POST, instance=preset)
        if form.is_valid():
            form.save()
            request.session["msg"] = "Das Preset wurde erfolgreich aktualisiert."
            return redirect('ui_presets')

    return render(request, "ui/preset_form.html", {"preset": preset, "form": form, "mode": "edit"})


@login_required
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
def preset_delete(request, id):
    preset = get_object_or_404(Preset, pk=id)
    preset.delete()
    request.session["msg"] = "Das Preset wurde erfolgreich gelöscht."
    return redirect("ui_presets")


@login_required
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
def item_view(request, id):
    item = get_object_or_404(Item, pk=id)
    context = {
        "item": item
    }
    return render(request, "ui/item_view.html", context)


@login_required
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
def item_delete(request, id):
    item = get_object_or_404(Item, pk=id)
    item.delete()
    request.session["msg"] = "Das Objekt wurde erfolgreich gelöscht."
    return redirect("ui_items")


@login_required
def item_barcode(request, id):
    item = get_object_or_404(Item, pk=id)
    filename = barcode_pdf(item)
    f = open(filename, "rb")
    return FileResponse(f, content_type="application/pdf")


@login_required
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
def person_view(request, id):
    person = get_object_or_404(Person, pk=id)
    context = {
        "person": person
    }
    return render(request, "ui/person_view.html", context)


@login_required
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
def person_delete(request, id):
    person = get_object_or_404(Person, pk=id)
    person.delete()
    request.session["msg"] = "Die Person wurde erfolgreich gelöscht."
    return redirect("ui_persons")


@login_required
def check_out(request):
    msg = False
    msg_type = "success"
    step = request.session["step"] if request.session.get("step", False) else 1
    if step > 1:
        process = CheckOutProcess.objects.get(id=request.session["process"])

    if request.method == "POST":

        # Cancel checkout
        if request.POST.get("cancel", False):
            print("Cancelling")
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
            print("Suche Person")
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

    print(step)

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
def loan_form(request, id):
    process = get_object_or_404(CheckOutProcess, pk=id)
    filename = loan_form_pdf(process)
    f = open(filename, "rb")
    return FileResponse(f, content_type="application/pdf")


@login_required
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
def check_view(request, id):
    check = get_object_or_404(CheckOutProcess, pk=id, is_check_out_in_process=False)
    context = {
        "check": check
    }
    return render(request, "ui/check_view.html", context)


@login_required
def check_in(request):
    context = {}
    msg = False
    if request.method == "POST" and request.POST.get("scan", False):
        scan = request.POST["scan"]
        check = None
        print(scan)
        try:
            id = int(scan)
            check = Check.objects.get(item_id=id, checked_in=False)
        except (Check.DoesNotExist, ValueError):
            try:
                check = Check.objects.get(item__barcode=scan, checked_in=False)
            except Check.DoesNotExist:
                msg = "not_found"

        if not msg:
            print("Go on")
            check.checked_in = True
            check.checked_in_at = timezone.now()
            check.checked_in_by = request.user
            check.save()
            context["check"] = check
            msg = "checked_in"

    context["msg"] = msg
    return render(request, "ui/check-in.html", context)


@login_required
def check_in_confirmation(request, id):
    process = get_object_or_404(CheckOutProcess, pk=id)
    filename = check_in_confirmation_pdf(process)
    f = open(filename, "rb")
    return FileResponse(f, content_type="application/pdf")
