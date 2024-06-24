# reservation_app/serializers.py

from rest_framework import serializers
from .models import Reservation

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
        extra_kwargs = {
            'prix_ticket': {'required': False},
            'client': {'required': False},
            'flight': {'required': False},
            'is_paid': {'required': False}
        }
