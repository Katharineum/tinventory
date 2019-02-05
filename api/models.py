from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    # icon = models.CharField()

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField(unique=True, blank=True)

    def __str__(self):
        return self.name

# Create your models here.

# class Model(models.Model):
#     name = models.CharField()
#     manufacturer = models.CharField(blank=True)
#     link = models.URLField(blank=True)
#     description = models.TextField(blank=True)
