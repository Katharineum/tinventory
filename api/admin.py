from django.contrib import admin

# Register your models here.
from api.models import Category, Location, Preset, Item, Person, CheckOutProcess, Check

admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Preset)
admin.site.register(Item)
admin.site.register(Person)
admin.site.register(CheckOutProcess)
admin.site.register(Check)
