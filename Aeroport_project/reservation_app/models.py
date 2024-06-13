from django.db import models
from django.utils import timezone

class Reservation(models.Model):
    client_id = models.ForeignKey('client_app.Clients', on_delete=models.CASCADE)
    flight_id = models.ForeignKey('vols_depart_app.FlightDeparture', on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    prix_ticket = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Reservation for flight {self.flight_id}"

    def __repr__(self):
        return f"Reservation for flight {self.flight_id}"
