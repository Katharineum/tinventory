from django.contrib import admin

# Register your models here.
from api.models import Category, Location

admin.site.register(Category)
admin.site.register(Location)