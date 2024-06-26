# Generated by Django 5.0 on 2024-06-20 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vols_arriver_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='flightarrival',
            name='prix',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='flightarrival',
            name='sieges_disponible',
            field=models.PositiveIntegerField(default=100),
        ),
    ]
