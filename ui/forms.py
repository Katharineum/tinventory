from django.forms import ModelForm

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
