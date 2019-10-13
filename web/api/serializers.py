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

from api.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("id", 'username', "first_name", "last_name")


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "name")


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name",)


class CheckProcessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CheckOutProcess
        fields = "__all__"


class PresetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Preset
        fields = ("id", "name", "manufacturer", "description")


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    preset = PresetSerializer(many=False, read_only=True)

    class Meta:
        model = Item
        fields = "__all__"


class CheckSerializer(serializers.HyperlinkedModelSerializer):
    item = ItemSerializer(many=False, read_only=True)

    class Meta:
        model = Check
        fields = "__all__"