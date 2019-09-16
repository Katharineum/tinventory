from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form
from django import forms

from api.models import Category, Location, Preset, Item


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


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ("barcode", "name", "category", "preset", "notes", "location")


class InventoryForm(Form):
    barcode = forms.CharField(label="Barcode", required=False)
    category_select = forms.ModelChoiceField(Category.objects.all(), label="Kategorie auswählen", required=True)
    category_new = forms.CharField(label="neue Kategorie erstellen", required=False)
    preset_select = forms.ModelChoiceField(Preset.objects.all(), label="Preset auswählen", required=False)
    preset_new_name = forms.CharField(label="Name des Preset", required=False)
    preset_new_manufacturer = forms.CharField(label="Hersteller des Preset", required=False)
    name = forms.CharField(required=True, label="Bezeichnung")
    notes = forms.CharField(widget=forms.Textarea, label="Notizen", required=False)
    location = forms.ModelChoiceField(Location.objects.all(), label="Ort", required=True)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["category_select"] is None and cleaned_data["category_new"] == "":
            return ValidationError("Es wird eine Kategorie benötigt.")

        # if cleaned_data["preset_select"] is None and cleaned_data["preset_new_name"] == "":
        #     return ValidationError("Es wird")

    def save(self):
        data = self.cleaned_data
        if data["category_select"] is not None:
            category = data["category_select"]
            print(category)
        else:
            category = Category.objects.create(name=data["category_name"])

        if data["preset_select"] is not None:
            preset = data["preset_select"]

        elif data["preset_new_name"] != "":
            preset = Preset.objects.create(name=data["preset_new_name"], manufacturer=data["preset_new_manufacturer"])
        else:
            preset = None

        return Item.objects.create(name=data["name"], notes=data["notes"], location=data["location"], category=category,
                                   preset=preset, barcode=data["barcode"])
