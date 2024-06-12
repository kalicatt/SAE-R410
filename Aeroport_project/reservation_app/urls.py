from django.urls import path
from .views import ReservationListAPIView, ReservationDetailAPIView

uurlpatterns = [
    path('reservations/', ReservationListAPIView.as_view(), name='reservation-list'),
    path('reservations/<int:pk>/', ReservationDetailAPIView.as_view(), name='reservation-detail'),

]