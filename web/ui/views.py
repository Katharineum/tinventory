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
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Model
from django.forms import Form
from django.http import (
    FileResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from api.models import Category, Check, CheckOutProcess, Item, Location, Person, Preset
from api.reports import (
    barcode_pdf,
    check_in_confirmation_pdf,
    excuse_form_pdf,
    loan_form_pdf,
)
from ui.forms import (
    CategoryForm,
    CheckForm,
    ExcuseForm,
    InventoryForm,
    ItemForm,
    LocationForm,
    PersonForm,
    PresetForm,
)


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


class StandardListView(ListView, LoginRequiredMixin, PermissionRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.session.get("msg", False):
            context["msg"] = self.request.session["msg"]
            self.request.session["msg"] = None
        return context


class StandardDetailView(DetailView, LoginRequiredMixin, PermissionRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.session.get("msg", False):
            context["msg"] = self.request.session["msg"]
            self.request.session["msg"] = None
        return context


class InstanceMixin(object):
    @property
    def pk(self):
        return self.kwargs["id"]

    @property
    def instance(self):
        return get_object_or_404(self.model_class, pk=self.pk)


class StandardNewView(View, LoginRequiredMixin, PermissionRequiredMixin):
    form_class: Form = Form
    template_name: str = "form.html"
    redirect_url: str = "ui_index"
    redirect_with_id: bool = False
    success_message: str = _("Creating was successfully.")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form, "mode": "new"})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            instance = form.save()
            request.session["msg"] = self.success_message
            if self.redirect_with_id:
                return redirect(self.redirect_url, instance.id)
            else:
                return redirect(self.redirect_url)
        return render(request, self.template_name, {"form": form, "mode": "new"})


class StandardEditView(
    View, LoginRequiredMixin, PermissionRequiredMixin, InstanceMixin
):
    form_class: Form = Form
    model_class: Model = Model
    template_name: str = "form.html"
    redirect_url: str = "ui_index"
    redirect_with_id: bool = False
    success_message: str = _("Updating was successfully.")

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.instance)
        return render(
            request,
            self.template_name,
            {"form": form, "mode": "edit", "instance": self.instance},
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.instance)
        if form.is_valid():
            form.save()
            request.session["msg"] = self.success_message

            if self.redirect_with_id:
                return redirect(self.redirect_url, self.instance.id)
            else:
                return redirect(self.redirect_url)

        return render(
            request,
            self.template_name,
            {"form": form, "mode": "edit", "instance": self.instance},
        )


class StandardDeleteView(
    View, LoginRequiredMixin, PermissionRequiredMixin, InstanceMixin
):
    model_class: Model = Model
    redirect_url: str = "ui_index"
    success_message: str = _("Deleting was successfully.")

    def get(self, request, *args, **kwargs):
        self.instance.delete()
        request.session["msg"] = self.success_message
        return redirect(self.redirect_url)


class CategoryList(StandardListView):
    model = Category
    template_name = "ui/category_list.html"
    permission_required = "api.view_category"


class CategoryNewView(StandardNewView):
    form_class = CategoryForm
    template_name = "ui/category_form.html"
    redirect_url = "ui_categories"
    success_message = _("Category was created successfully.")
    permission_required = "api.add_category"


class CategoryEditView(StandardEditView):
    form_class = CategoryForm
    model_class = Category
    template_name = "ui/category_form.html"
    redirect_url = "ui_categories"
    success_message = _("Category was updated successfully.")
    permission_required = "api.change_category"


class CategoryDeleteView(StandardDeleteView):
    model_class = Category
    redirect_url = "ui_categories"
    success_message = _("Category was deleted successfully.")
    permission_required = "api.delete_category"


#############
# LOCATIONS #
#############


class LocationListView(StandardListView):
    model = Location
    template_name = "ui/location_list.html"
    permission_required = "api.view_location"


class LocationEditView(StandardEditView):
    form_class = LocationForm
    model_class = Location
    template_name = "ui/location_form.html"
    redirect_url = "ui_locations_detail"
    redirect_with_id = True
    success_message = _("Location was updated successfully.")
    permission_required = "api.change_location"


class LocationDetailView(StandardDetailView):
    model = Location
    template_name = "ui/location_detail.html"
    permission_required = "api.view_location"


@login_required
@permission_required("api.change_item")
def location_add_item(request, pk):
    if request.method == "GET":
        if "barcode" in request.GET.keys():
            try:
                barcode = request.GET["barcode"]

                try:
                    id = int(barcode)
                    item = Item.objects.get(id=id)
                except (Item.DoesNotExist, ValueError):
                    try:
                        item = Item.objects.get(barcode=barcode)
                    except Item.DoesNotExist:
                        give_location_error(
                            400, _("No item with this barcode was found.")
                        )
                        return

                location = Location.objects.get(pk=pk)

                if item.location != location:

                    item.location = location

                    item.save()
                    location.save()

                    status = 200
                    data = {"status": "success", "status_code": 200}
                else:
                    status, data = give_location_error(
                        400, _("Item is already at this location.")
                    )

            except Item.DoesNotExist:
                status, data = give_location_error(
                    400, _("Barcode is not valid.")
                )  # 400 - bad request
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed(["GET"])
    return JsonResponse(data=data, status=status)


def give_location_error(code: int, msg: str):
    status = 200
    data = {"status": "error", "status_code": code, "message": msg}

    return status, data


class LocationNewView(StandardNewView):
    form_class = LocationForm
    template_name = "ui/location_form.html"
    redirect_with_id = True
    redirect_url = "ui_locations_detail"
    success_message = _("Location was created successfully.")
    permission_required = "api.add_location"


class LocationDeleteView(StandardDeleteView):
    model_class = Location
    redirect_url = "ui_locations"
    success_message = _("Location was deleted successfully.")
    permission_required = "api.delete_location"


###########
# PRESETS #
###########


class PresetListView(StandardListView):
    model = Preset
    template_name = "ui/preset/list.html"
    permission_required = "api.view_preset"


class PresetDetailView(StandardDetailView):
    model = Preset
    template_name = "ui/preset/detail.html"
    permission_required = "api.view_preset"


class PresetEditView(StandardEditView):
    form_class = PresetForm
    model_class = Preset
    template_name = "ui/preset/form.html"
    redirect_url = "ui_presets_view"
    redirect_with_id = True
    success_message = _("Preset was updated successfully.")
    permission_required = "api.change_preset"


class PresetNewView(StandardNewView):
    form_class = PresetForm
    template_name = "ui/preset/form.html"
    redirect_url = "ui_presets_view"
    redirect_with_id = True
    success_message = _("Preset was created successfully.")
    permission_required = "api.add_preset"


class PresetDeleteView(StandardDeleteView):
    model_class = Preset
    redirect_url = "ui_presets"
    success_message = _("Preset was deleted successfully.")
    permission_required = "api.delete_preset"


class ItemListView(StandardListView):
    model = Item
    template_name = "ui/item/list.html"
    permission_required = "api.view_item"


class ItemDetailView(StandardDetailView):
    model = Item
    template_name = "ui/item/view.html"
    permission_required = "api.view_item"


class ItemEditView(StandardEditView):
    form_class = ItemForm
    model_class = Item
    template_name = "ui/item/form.html"
    redirect_with_id = True
    redirect_url = "ui_items_view"
    success_message = _("Item was updated successfully.")
    permission_required = "api.change_item"


class ItemNewView(StandardNewView):
    form_class = ItemForm
    template_name = "ui/item/form.html"
    redirect_url = "ui/item/view.html"
    redirect_with_id = True
    success_message = _("Item was created successfully.")
    permission_required = "api.add_item"


class ItemDeleteView(StandardDeleteView):
    model_class = Item
    redirect_url = "ui_items"
    success_message = _("Item was deleted successfully. ")


class PDFResponse(FileResponse):
    def __init__(self, filename: str, **kwargs):
        f = open(filename, "rb")
        FileResponse.__init__(self, f, content_type="application/pdf", **kwargs)


@login_required
@permission_required("api.view_item")
def item_barcode(request, id):
    item = get_object_or_404(Item, pk=id)
    filename = barcode_pdf(item)
    return PDFResponse(filename)


@login_required
@permission_required("api.add_item")
def inventory(request):
    context = {}
    if request.method == "GET":
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


class PersonListView(StandardListView):
    model = Person
    template_name = "ui/person/list.html"
    permission_required = "api.view_person"


class PersonDetailView(StandardDetailView):
    model = Person
    template_name = "ui/person/detail.html"
    permission_required = "api.view_person"


class PersonEditView(StandardEditView):
    form_class = PersonForm
    model_class = Person
    template_name = "ui/person/form.html"
    redirect_url = "ui_persons_view"
    redirect_with_id = True
    success_message = _("Person was updated successfully.")
    permission_required = "api.change_person"


class PersonNewView(StandardNewView):
    form_class = PersonForm
    template_name = "ui/person/form.html"
    redirect_with_id = True
    redirect_url = "ui_persons_view"
    success_message = _("Person was created successfully.")
    permission_required = "api.add_person"


class PersonDeleteView(StandardDeleteView):
    model_class = Person
    redirect_url = "ui_persons"
    success_message = _("Person was deleted successfully.")
    permission_required = "api.delete_person"


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
            process = CheckOutProcess.objects.create(
                borrowing_person=person, lending_user=request.user
            )
            request.session["process"] = process.id
            request.session["step"] = 2
            step = 2

        if step == 1 and request.POST.get("create-person", False):
            # Create person
            if request.POST["create-person"] != "":
                person = Person.objects.create(name=request.POST["create-person"])
            else:
                return redirect("ui_check_out")
            process = CheckOutProcess.objects.create(
                borrowing_person=person, lending_user=request.user
            )
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
                msg = _(
                    "Object was removed from check out list successfully."
                )  # "Das Objekt wurde erfolgreich von der Check-Out-Liste entfernt."
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
                    msg = "Es gibt kein Objekt mit der ID oder dem Barcode {}.".format(
                        scan
                    )
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

        if (
            step == 2
            and request.POST.get("confirm", False)
            and process.checks.count() > 0
        ):
            request.session["step"] = 3
            step = 3

        elif step == 3 and process.checks.count() > 0:
            form = CheckForm(request.POST, instance=process)
            if form.is_valid():
                process.condition = form.cleaned_data["condition"]
                process.check_in_until = form.cleaned_data["check_in_until"]
                process.is_check_out_in_process = False
                process.checked_out_at = timezone.now()
                process.save()
                del request.session["step"]
                del request.session["process"]
                step = 4

    if step == 1:
        technicians = Person.objects.all().filter(is_technician=True).order_by("name")
        persons = Person.objects.all().filter(is_technician=False).order_by("name")
        return render(
            request,
            "ui/check-out-1.html",
            context={"technicians": technicians, "persons": persons},
        )
    elif step == 2:
        return render(
            request,
            "ui/check-out-2.html",
            context={"process": process, "msg": msg, "msg_type": msg_type},
        )
    elif step == 3:
        form = CheckForm(instance=process)
        return render(
            request, "ui/check-out-3.html", context={"process": process, "form": form}
        )
    elif step == 4:
        return render(request, "ui/check-out-done.html", context={"process": process})


@login_required
@permission_required("api.check_out")
def loan_form(request, id):
    process = get_object_or_404(CheckOutProcess, pk=id)
    filename = loan_form_pdf(process)
    return PDFResponse(filename)


@login_required
@permission_required("api.check_out")
def checks(request):
    checks = CheckOutProcess.objects.all().filter(is_check_out_in_process=False)
    context = {"checks": checks}
    if request.session.get("msg", False):
        context["msg"] = request.session["msg"]
        request.session["msg"] = None

    return render(request, "ui/checks.html", context)


@login_required
@permission_required("api.check_out")
def check_view(request, id):
    check = get_object_or_404(CheckOutProcess, pk=id, is_check_out_in_process=False)
    context = {"check": check}
    if request.session.get("msg", False):
        context["msg"] = request.session["msg"]
        request.session["msg"] = None
    return render(request, "ui/check_view.html", context)


@login_required
@permission_required("api.check_out")
def check_edit(request, id):
    check = get_object_or_404(CheckOutProcess, pk=id)

    if request.method == "GET":
        form = CheckForm(instance=check)
    else:
        form = CheckForm(request.POST, instance=check)
        if form.is_valid():
            form.save()
            request.session[
                "msg"
            ] = "Die Rückgabebedingungen wurden erfolgreich aktualisiert."
            return redirect("ui_checks_view", check.id)

    return render(request, "ui/person/form.html", {"check": check, "form": form})


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
    return PDFResponse(filename)


@login_required
def excuse(request):
    if request.method == "GET":
        form = ExcuseForm()
    else:
        form = ExcuseForm(request.POST)
        if form.is_valid():
            filename = excuse_form_pdf(
                form.cleaned_data["technician"],
                form.cleaned_data["date"],
                form.cleaned_data["start"],
                form.cleaned_data["stop"],
                form.cleaned_data["reason"],
            )

            return PDFResponse(filename)

    return render(request, "ui/excuse.html", context={"form": form})


def license(request):
    LICENSE_APACHE_2 = "Apache 2.0 License"
    LICENSE_BSD = "2-Clause BSD License"
    LICENSE_BSD_3 = "3-Clause BSD License"
    LICENSE_MIT = "MIT License"

    components = [
        (
            "Docker (u.a. Engine, CLI, docker-compose)",
            "https://github.com/docker",
            LICENSE_APACHE_2,
            "https://github.com/docker/docker/blob/master/LICENSE",
        ),
        (
            "Django",
            "https://www.djangoproject.com/",
            "Django BSD License",
            "https://github.com/django/django/blob/master/LICENSE",
        ),
        (
            "Python 3",
            "https://www.python.org/",
            "PSF LICENSE AGREEMENT FOR PYTHON",
            "https://docs.python.org/3/license.html",
        ),
        (
            "Bootstrap",
            "https://getbootstrap.com/",
            LICENSE_MIT,
            "https://github.com/twbs/bootstrap/blob/master/LICENSE",
        ),
        (
            "jQuery",
            "https://jquery.com/",
            LICENSE_MIT,
            "https://github.com/jquery/jquery/blob/master/LICENSE.txt",
        ),
        (
            "FontAwesome Icon Font",
            "https://github.com/FortAwesome/Font-Awesome",
            "SIL OFL 1.1 License",
            "https://scripts.sil.org/OFL",
        ),
        (
            "DataTables",
            "https://datatables.net",
            LICENSE_MIT,
            "https://datatables.net/license/mit",
        ),
        (
            "pip",
            "https://pypi.org/project/pip/",
            LICENSE_MIT,
            "https://github.com/pypa/pip/blob/master/LICENSE.txt",
        ),
        (
            "requests",
            "https://requests.kennethreitz.org/",
            LICENSE_APACHE_2,
            "https://github.com/psf/requests/blob/master/LICENSE",
        ),
        (
            "django-bootstrap-form",
            "https://github.com/tzangms/django-bootstrap-form",
            LICENSE_BSD_3,
            "https://github.com/tzangms/django-bootstrap-form/blob/master/LICENSE",
        ),
        (
            "django-cors-headers",
            "https://github.com/adamchainz/django-cors-headers",
            LICENSE_MIT,
            "https://github.com/adamchainz/django-cors-headers/blob/master/LICENSE",
        ),
        (
            "django-oauth-toolkit",
            "https://github.com/jazzband/django-oauth-toolkit",
            LICENSE_BSD,
            "https://github.com/jazzband/django-oauth-toolkit/blob/master/LICENSE",
        ),
        (
            "django-widget-tweaks",
            "https://github.com/jazzband/django-widget-tweaks",
            LICENSE_MIT,
            "https://github.com/jazzband/django-widget-tweaks/blob/master/LICENSE",
        ),
        (
            "djangorestframework",
            "https://www.django-rest-framework.org/",
            LICENSE_BSD_3,
            "https://www.django-rest-framework.org/#license",
        ),
        (
            "fpdf (PyFPDF)",
            "https://github.com/reingart/pyfpdf",
            "GNU Lesser General Public License v3.0",
            "https://github.com/reingart/pyfpdf/blob/master/LICENSE",
        ),
        (
            "Django-Select2",
            "https://github.com/codingjoe/django-select2",
            "MIT License",
            "https://github.com/codingjoe/django-select2/blob/master/LICENSE",
        ),
    ]
    components.sort(key=lambda elem: elem[0].lower())
    return render(request, "ui/license.html", context={"components": components})
