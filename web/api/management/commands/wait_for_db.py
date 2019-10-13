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

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Checking the connection to the database.')
        database_connected = False
        while not database_connected:
            try:
                connection.ensure_connection()
                database_connected = True
            except OperationalError:
                print(self.style.ERROR(
                    "Database still unavailable."),
                    end='')
                print(" Waiting 1 second.")
                time.sleep(1)
        print(self.style.SUCCESS('Database available!'))
