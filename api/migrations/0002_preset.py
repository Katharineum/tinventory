# Generated by Django 2.1.5 on 2019-03-16 16:37

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('manufacturer', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('category',
                 models.ForeignKey(default=api.models.default_preset, on_delete=django.db.models.deletion.SET_DEFAULT,
                                   to='api.Category')),
            ],
        ),
    ]