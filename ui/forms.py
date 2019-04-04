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
        fields = ("name", "category", "preset", "notes", "location")


class InventoryForm(Form):
    category_select = forms.ModelChoiceField(Category.objects.all(), label="Kategorie auswählen")
    category_new = forms.CharField(label="neue Kategorie erstellen")
    preset_select = forms.ModelChoiceField(Preset.objects.all(), label="Preset auswählen")
    preset_new_name = forms.CharField(label="Name des Preset")
    preset_new_manufacturer = forms.CharField(label="Hersteller des Preset", required=False)
    name = forms.CharField(required=True, label="Bezeichnung")
    notes = forms.CharField(widget=forms.Textarea, label="Notizen", required=False)
    location = forms.ModelChoiceField(Location.objects.all(), label="Ort", required=True)
