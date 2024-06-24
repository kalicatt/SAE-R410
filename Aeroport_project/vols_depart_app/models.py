# vols_arriver_app/models.py

from django.db import models
from datetime import datetime
from django.utils.timezone import make_naive

class FlightDeparture(models.Model):
    flight_number = models.CharField(max_length=50)
    departure_time = models.DateTimeField()
    destination = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    sieges_disponible = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.flight_number

    def __repr__(self):
        return self.flight_number

    @property
    def formatted_departure_time(self):
        naive_time = make_naive(self.departure_time)  # Convert to naive datetime
        return naive_time.strftime('%d/%m/%Y %H:%M')
