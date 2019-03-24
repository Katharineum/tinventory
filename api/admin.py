from django.contrib import admin

# Register your models here.
from api.models import Category, Location, Preset, Item

admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Preset)
admin.site.register(Item)
