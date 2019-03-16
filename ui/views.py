from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from api.models import Category, Location
from ui.forms import CategoryForm, LocationForm


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
            name = form.cleaned_data['name']
            Category.objects.filter(id=id).update(name=name)
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
            name = form.cleaned_data['name']
            Category.objects.create(name=name)
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
            name = form.cleaned_data['name']
            number = form.cleaned_data["number"]
            Location.objects.filter(id=id).update(name=name, number=number)
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
            name = form.cleaned_data['name']
            number = form.cleaned_data["number"]
            Location.objects.create(name=name, number=number)
            request.session["msg"] = "Der Ort wurde erfolgreich erstellt."
            return redirect('ui_locations')

    return render(request, "ui/location_form.html", {"form": form, "mode": "new"})


@login_required
def location_delete(request, id):
    location = get_object_or_404(Location, pk=id)
    location.delete()
    request.session["msg"] = "Der Ort wurde erfolgreich gelöscht."
    return redirect("ui_locations")
