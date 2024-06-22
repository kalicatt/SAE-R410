# reservation_app/serializers.py

from rest_framework import serializers
from .models import Reservation

class ReservationSerializer(serializers.ModelSerializer):
    client_email = serializers.EmailField(source='client.email', read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'
