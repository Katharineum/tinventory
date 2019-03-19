from django.db import models


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
    number = models.IntegerField(unique=True, blank=True, verbose_name="Schranknummer")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ort"
        verbose_name_plural = "Orte"


def default_preset():
    return Category.objects.get_or_create(name="Sonstiges")


class Preset(models.Model):
    name = models.CharField(max_length=200, verbose_name="Bezeichnung")
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name="Hersteller")
    description = models.TextField(blank=True, verbose_name="Beschreibung")
    category = models.ForeignKey(Category, models.SET_DEFAULT, default=default_preset, verbose_name="Kategorie")
    image = models.ImageField(upload_to="images/presets/", blank=True, verbose_name="Bild")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Preset"
        verbose_name_plural = "Presets"
