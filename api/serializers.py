from django.contrib.auth.models import User, Group
from rest_framework import serializers

from api.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", 'username', "first_name", "last_name")


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "name")


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name",)


class CheckProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckOutProcess
        # fields = ("id", "borrowing_person", "lending_user")
        fields = "__all__"


class PresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preset
        fields = ("id", "name", "manufacturer", "description")


class ItemSerializer(serializers.ModelSerializer):
    preset = PresetSerializer(many=False, read_only=True)

    class Meta:
        model = Item
        fields = "__all__"


class CheckSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False, read_only=True)

    class Meta:
        model = Check
        fields = "__all__"
