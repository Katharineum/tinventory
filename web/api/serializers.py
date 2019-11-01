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

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField

from api.models import *


# TODO: Create serializers for all models, resolving location, category, preset, etc.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("url", "id", 'username', "first_name", "last_name")


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ("url", "id", "name")


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ("url", "id", "name",)


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    # preset = PresetSerializer(many=False, read_only=True)

    class Meta:
        model = Location
        # fields = "__all__"
        exclude = ["url"]


class CheckProcessSerializer(serializers.HyperlinkedModelSerializer):
    # loan_form = HyperlinkedIdentityField(view_name="ui_loan_form")

    class Meta:
        model = CheckOutProcess
        fields = ["url", "id", "checked_out_at", "is_check_out_in_process", "check_in_until", "borrowing_person",
                  "lending_user"]


class PresetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Preset
        fields = ("id", "name", "manufacturer", "description")


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    preset = PresetSerializer(many=False, read_only=True)
    location = LocationSerializer(many=False, read_only=True)

    class Meta:
        model = Item
        # fields = "__all__"
        exclude = ["url"]
        # fields = ["id", "url", "preset", "location", "name", "barcode", "notes", "last_time_seen_at", "category"]


class CheckSerializer(serializers.HyperlinkedModelSerializer):
    item = ItemSerializer(many=False, read_only=True)
    check_out = CheckProcessSerializer(many=False, read_only=True)

    class Meta:
        model = Check
        fields = ("id", "url", "item", "checked_in", "checked_in_at", "check_out", "checked_in_by")
