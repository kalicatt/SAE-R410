# Generated by Django 5.0.6 on 2024-06-13 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paiement_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paiement',
            name='montant',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
