# Generated by Django 5.0 on 2024-06-22 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='client_email',
            field=models.EmailField(default=1, max_length=254),
            preserve_default=False,
        ),
    ]