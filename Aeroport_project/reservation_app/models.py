from django.db import models

class Reservation(models.Model):
    client_id = models.ForeignKey('client_app.Clients', on_delete=models.CASCADE)
    flight_id = models.IntegerField()
    reservation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation for flight {self.flight_id}"

    def __repr__(self):
        return f"Reservation for flight {self.flight_id}"
