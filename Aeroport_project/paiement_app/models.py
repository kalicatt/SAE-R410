# paiement_app/models.py

from django.db import models
from client_app.models import Clients
from reservation_app.models import Reservation

class Paiement(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    client_email = models.EmailField()  # Nouveau champ pour l'email du client
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    paiement_date = models.DateTimeField(auto_now_add=True)
    paiement_methode = models.CharField(max_length=50)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f'Paiement {self.id} by {self.client.nom}'
