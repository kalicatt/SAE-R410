# reservation_app/urls.py

from django.urls import path
from .views import ReservationListAPIView, ReservationDetailAPIView, admin_reservations, validate_reservation, ReservationDetailView

urlpatterns = [
    path('reservations/', ReservationListAPIView.as_view(), name='reservation-list'),
    path('reservations/<int:pk>/', ReservationDetailAPIView.as_view(), name='reservation-detail'),
    path('admin_reservations/', admin_reservations, name='admin_reservations'),
    path('admin_reservations/validate/<int:reservation_id>/', validate_reservation, name='validate_reservation'),
    path('reservations/update/<int:pk>/', ReservationDetailView.as_view(), name='reservation-update'),
]
