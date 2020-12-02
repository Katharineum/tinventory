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

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name", blank=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"


class Location(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    number = models.IntegerField(unique=True, blank=True, null=True, verbose_name="Schranknummer")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Ort"
        verbose_name_plural = "Orte"


def default_category():
    return Category.objects.get_or_create(name="Sonstiges")[0]


class Preset(models.Model):
    name = models.CharField(max_length=200, verbose_name="Bezeichnung")
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name="Hersteller")
    description = models.TextField(blank=True, verbose_name="Beschreibung")
    category = models.ForeignKey(Category, models.SET_DEFAULT, default=default_category, verbose_name="Kategorie",
                                 related_name="presets")
    image = models.ImageField(upload_to="images/presets/", blank=True, verbose_name="Bild")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Preset"
        verbose_name_plural = "Presets"


class Item(models.Model):
    name = models.CharField(max_length=200, verbose_name="Bezeichnung")
    barcode = models.CharField(max_length=15, verbose_name="Barcode", null=True, blank=True,
                               help_text="Frei lassen, um Barcode automatisch zu generieren", unique=True)

    category = models.ForeignKey(Category, models.SET_DEFAULT, default=default_category, verbose_name="Kategorie",
                                 related_name="items")
    preset = models.ForeignKey(Preset, models.SET_NULL, blank=True, null=True, verbose_name="Preset",
                               related_name="items")

    notes = models.TextField(blank=True, verbose_name="Notizen")

    location = models.ForeignKey(Location, models.SET_NULL, blank=True, null=True, verbose_name="Ort",
                                 related_name="items")
    last_time_seen_at = models.DateTimeField(auto_now=True, verbose_name="Letztes Mal gesehen am")

    def gen_barcode(self):
        if self.id:
            id = self.id
        else:
            id = Item.get_next_item_id()
        return "{num:05d}".format(num=id)

    @staticmethod
    def get_next_item_id():
        id_max = Item.objects.all().aggregate(Max('id'))['id__max']
        return id_max + 1 if id_max else 1

    def is_available(self):
        if self.checks.filter(checked_in=False).count() > 0:
            return False
        else:
            return True

    def get_checks(self):
        if not self.is_available():
            return self.checks.filter(checked_in=False).all()
        else:
            return []

    def save(self, *args, **kwargs):
        if self.barcode == "" or self.barcode is None:
            self.barcode = self.gen_barcode()

        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        if self.preset:
            return "{} ({})".format(self.name, self.preset)
        else:
            return self.name

    class Meta:
        ordering = ["name", "preset__name"]
        verbose_name = "Objekt"
        verbose_name_plural = "Objekte"


class Person(models.Model):
    name = models.CharField(max_length=200, blank=False, verbose_name="Name")
    email = models.EmailField(verbose_name="E-Mail", blank=True)

    notes = models.TextField(blank=True, verbose_name="Notizen")
    is_within_school = models.BooleanField(verbose_name="Schulintern?", default=False)
    is_technician = models.BooleanField(verbose_name="Aktiver Techniker?", default=False)

    def get_checks(self):
        checks = []
        for check_out in self.check_outs.all():
            checks += check_out.checks.all()
        print(checks)
        return checks

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Person"
        verbose_name_plural = "Personen"


class CheckOutCondition(models.Model):
    default = models.BooleanField(verbose_name="Standard")
    text = models.TextField(verbose_name="Text")

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["text"]
        verbose_name = "Check-Out-Bedingung"
        verbose_name_plural = "Check-Out-Bedingungen"

    def save(self, *args, **kwargs):
        if self.default:
            # select all other active items
            qs = CheckOutCondition.objects.filter(default=True)
            # except self (if self already exists)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            # and deactive them
            qs.update(default=False)

        super(CheckOutCondition, self).save(*args, **kwargs)


class CheckOutProcess(models.Model):
    borrowing_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="check_outs",
                                         verbose_name="Ausleihende Person")
    lending_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="check_outs",
                                     verbose_name="Verleihender Nutzer")
    checked_out_at = models.DateTimeField(auto_now_add=True, verbose_name="Check-Out-Zeitpunkt")
    is_check_out_in_process = models.BooleanField(default=True, verbose_name="Check-Out im Prozess?")
    check_in_until = models.DateField(verbose_name="Check-In bis", blank=True, null=True)
    condition = models.ForeignKey(CheckOutCondition, on_delete=models.SET_NULL, verbose_name="Check-Out-Bedingung",
                                  blank=True, null=True)

    def is_everything_checked_in(self):
        return self.checks.filter(checked_in=False).count() <= 0

    def is_in_time(self):
        if self.check_in_until:
            return self.check_in_until >= timezone.now().date()
        else:
            return True

    def __str__(self):
        return "{} ({})".format(self.borrowing_person, self.checked_out_at)

    def save(self, *args, **kwargs):
        if self.condition is None:
            obj = CheckOutCondition.objects.all().filter(default=True)
            if obj.count() >= 1:
                self.condition = obj[0]

        super(CheckOutProcess, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-check_in_until", "-checked_out_at"]
        verbose_name = "Check-Out-Vorgang"
        verbose_name_plural = "Check-Out-Vorgänge"
        permissions = [("check_out", "Can check out things"), ("check_in", "Can check in things")]


class Check(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="checks", verbose_name="Objekt")
    check_out = models.ForeignKey(CheckOutProcess, on_delete=models.CASCADE, related_name="checks",
                                  verbose_name="Check-Out-Vorgang")
    checked_in = models.BooleanField(default=False, verbose_name="Check-In durchgeführt?")
    checked_in_at = models.DateTimeField(verbose_name="Check-In-Zeitpunkt", blank=True, null=True)
    checked_in_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="check_ins",
                                      verbose_name="Check-In durchgeführt von", blank=True, null=True)

    def __str__(self):
        return "{} [{}]".format(self.item, self.check_out)

    class Meta:
        ordering = ["-check_out__check_in_until", "-check_out__checked_out_at", "item__name", "item__preset__name"]
        verbose_name = "Check"
        verbose_name_plural = "Checks"
