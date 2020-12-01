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

from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form, TextInput, DateInput
from django import forms
from django_select2.forms import ModelSelect2Widget

from api.models import Category, Location, Preset, Item, Person, CheckOutProcess


class CategoryWidget(ModelSelect2Widget):
    search_fields = [
        "name__icontains",
    ]


class PresetWidget(ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "manufacturer__icontains",
        "description__icontains",
    ]


class LocationWidget(ModelSelect2Widget):
    search_fields = [
        "name__icontains",
    ]


class PersonWidget(ModelSelect2Widget):
    search_fields = [
        "name__icontains",
        "email__icontains",
        "notes__icontains",
    ]


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ("name",)


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ("name", "number")


class PresetForm(ModelForm):
    class Meta:
        model = Preset
        fields = ("name", "category", "description", "manufacturer", "image")
        widgets = {
            # "category": CategoryWidget,
        }


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ("barcode", "name", "category", "preset", "notes", "location")
        widgets = {
            # "category": CategoryWidget(),
            #     "preset": PresetWidget,
            #     "location": LocationWidget,
        }


class InventoryForm(Form):
    barcode = forms.CharField(label="Barcode", required=False)
    category_select = forms.ModelChoiceField(Category.objects.order_by("name").all(), label="Kategorie auswählen",
                                             required=False, widget=CategoryWidget)
    category_new = forms.CharField(label="neue Kategorie erstellen", required=False)
    preset_select = forms.ModelChoiceField(Preset.objects.all(), label="Preset auswählen", required=False,
                                           widget=PresetWidget)
    preset_new_name = forms.CharField(label="Name des Preset", required=False)
    preset_new_manufacturer = forms.CharField(label="Hersteller des Preset", required=False)
    name = forms.CharField(required=True, label="Bezeichnung")
    notes = forms.CharField(widget=forms.Textarea, label="Notizen", required=False)
    location = forms.ModelChoiceField(Location.objects.all(), label="Ort", required=True, widget=LocationWidget)

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)

        if cleaned_data.get("category_select", None) is None and cleaned_data["category_new"] == "":
            return ValidationError("Es wird eine Kategorie benötigt.")

        # if cleaned_data["preset_select"] is None and cleaned_data["preset_new_name"] == "":
        #     return ValidationError("Es wird")

    def save(self):
        data = self.cleaned_data
        if data.get("category_select", None) is not None:
            category = data["category_select"]
        else:
            category = Category.objects.create(name=data["category_new"])

        if data.get("preset_select", None) is not None:
            preset = data["preset_select"]

        elif data["preset_new_name"] != "":
            preset = Preset.objects.create(name=data["preset_new_name"], manufacturer=data["preset_new_manufacturer"],
                                           category=category)
        else:
            preset = None

        return Item.objects.create(name=data["name"], notes=data["notes"], location=data["location"], category=category,
                                   preset=preset, barcode=data["barcode"])


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = ("name", "email", "is_within_school", "is_technician", "notes")


class CheckForm(ModelForm):
    class Meta:
        model = CheckOutProcess
        fields = ("check_in_until", "condition")
        widgets = {
            "check_in_until": DateInput(attrs={"class": "datepicker-field"})
        }


HOURS = [(i, "{}. Stunde".format(i)) for i in range(1, 10)]


class ExcuseForm(Form):
    technician = forms.ModelChoiceField(Person.objects.filter(is_technician=True), label="Techniker", required=True,
                                        widget=PersonWidget)
    date = forms.DateField(label="Datum", required=True, widget=DateInput(attrs={"class": "datepicker-field"}))
    start = forms.ChoiceField(choices=HOURS, label="Von", required=True)
    stop = forms.ChoiceField(choices=HOURS, label="Bis", required=True)
    reason = forms.CharField(widget=forms.Textarea, label="Aufgaben", required=True)
