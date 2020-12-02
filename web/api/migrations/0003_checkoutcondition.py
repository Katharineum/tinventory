# Generated by Django 2.2.5 on 2019-11-02 10:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_auto_20191012_1658"),
    ]

    operations = [
        migrations.CreateModel(
            name="CheckOutCondition",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("default", models.BooleanField(unique=True, verbose_name="Standard")),
                ("text", models.TextField(verbose_name="Text")),
            ],
            options={
                "verbose_name": "Check-Out-Bedingung",
                "verbose_name_plural": "Check-Out-Bedingungen",
            },
        ),
    ]
