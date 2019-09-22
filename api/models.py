from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")

    # icon = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"


class Location(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    number = models.IntegerField(unique=True, blank=True, null=True, verbose_name="Schranknummer")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ort"
        verbose_name_plural = "Orte"


def default_category():
    return Category.objects.get_or_create(name="Sonstiges")


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

    # last_time_seen_by = models.ForeignKey

    def gen_barcode(self):
        return "OBJ{num:08d}".format(num=Item.get_next_item_id())

    @staticmethod
    def get_next_item_id():
        id_max = Item.objects.all().aggregate(Max('id'))['id__max']
        return id_max + 1 if id_max else 1

    def is_available(self):
        if self.checks.count() > 0:
            return False
        else:
            return True

    def get_check(self):
        if self.is_available():
            return self.checks.all()[0]
        else:
            return None

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

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Personen"


class CheckOutProcess(models.Model):
    borrowing_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="check_outs",
                                         verbose_name="Ausleihende Person")
    lending_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="check_outs",
                                     verbose_name="Verleihender Nutzer")
    checked_out_at = models.DateTimeField(auto_now_add=True, verbose_name="Check-Out-Zeitpunkt")
    is_check_out_in_process = models.BooleanField(default=True, verbose_name="Check-Out im Prozess?")
    check_in_until = models.DateField(verbose_name="Check-In bis", blank=True, null=True)

    def is_everything_checked_in(self):
        return self.checks.filter(checked_in=False).count() <= 0

    def is_in_time(self):
        if self.check_in_until:
            return self.check_in_until >= timezone.now().date()
        else:
            return True

    class Meta:
        verbose_name = "Check-Out-Vorgang"
        verbose_name_plural = "Check-Out-Vorgänge"


class Check(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="checks", verbose_name="Objekt")
    check_out = models.ForeignKey(CheckOutProcess, on_delete=models.CASCADE, related_name="checks",
                                  verbose_name="Check-Out-Vorgang")
    checked_in = models.BooleanField(default=False, verbose_name="Check-In durchgeführt?")
    checked_in_at = models.DateTimeField(verbose_name="Check-In-Zeitpunkt", blank=True, null=True)
    checked_in_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="check_ins",
                                      verbose_name="Check-In durchgeführt von", blank=True, null=True)

    class Meta:
        verbose_name = "Check"
        verbose_name_plural = "Checks"
