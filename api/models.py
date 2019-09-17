from django.db import models
from django.db.models import Max


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

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Personen"
