# Generated by Django 5.0.6 on 2024-06-13 10:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation_app', '0006_alter_reservation_prix_ticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='vol_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
