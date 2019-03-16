from django.forms import ModelForm

from api.models import Category


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ("name",)
