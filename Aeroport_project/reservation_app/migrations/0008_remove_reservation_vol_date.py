# Generated by Django 5.0.6 on 2024-06-13 10:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservation_app', '0007_reservation_vol_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='vol_date',
        ),
    ]
