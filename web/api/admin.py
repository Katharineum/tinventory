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

from django.contrib import admin

# Register your models here.
from api.models import Category, Location, Preset, Item, Person, CheckOutProcess, Check


class ItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Item._meta.fields if field.name != "id"]


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Preset)
admin.site.register(Item, ItemAdmin)
admin.site.register(Person)
admin.site.register(CheckOutProcess)
admin.site.register(Check)
