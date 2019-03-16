from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from api.models import Category
from ui.forms import CategoryForm


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
        # A POST request: Handle Form Upload
        # Bind data from request.POST into a PostForm
        form = CategoryForm(request.POST, instance=category)
        # If data is valid, proceeds to create a new post and redirect the user
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
        # A POST request: Handle Form Upload
        # Bind data from request.POST into a PostForm
        form = CategoryForm(request.POST)
        # If data is valid, proceeds to create a new post and redirect the user
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
