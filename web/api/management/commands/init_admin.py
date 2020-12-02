#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.count() == 0:
            new_admin = User.objects.create_superuser(
                username=os.getenv("TINVENTORY_SUPERUSER", "admin"),
                email=os.getenv("TINVENTORY_SUPERUSER_MAIL", "admin@example.com"),
                password=os.getenv("TINVENTORY_SUPERUSER_PASSWORD", "adminadmin"),
            )
            new_admin.save()
        else:
            print("Admin accounts can only be initialized if no Accounts exist")
