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

from django.test import TestCase

# Create your tests here.
from api.models import Category, Location


class CategoryTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test")

    def test_category_attr(self):
        """ Tests if name of category is equal """

        self.assertEqual(self.category.name, "Test")
        self.assertEqual(str(self.category), "Test")


class LocationTest(TestCase):
    def setUp(self):
        self.location = Location.objects.create(name="Test", number=1)
        self.location2 = Location.objects.create(name="Test2")

    def test_location_attr(self):
        """ Test if attributes of location are correct """

        self.assertEqual(self.location.name, "Test")
        self.assertEqual(str(self.location), "Test")
        self.assertEqual(self.location.number, 1)
        self.assertEqual(self.location2.name, "Test2")
        self.assertEqual(str(self.location2), "Test2")
        self.assertEqual(self.location2.number, None)
