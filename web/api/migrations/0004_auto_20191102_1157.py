# Generated by Django 2.2.5 on 2019-11-02 10:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_checkoutcondition"),
    ]

    operations = [
        migrations.AlterField(
            model_name="checkoutcondition",
            name="default",
            field=models.BooleanField(verbose_name="Standard"),
        ),
    ]
