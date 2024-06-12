from django.urls import path
from . import views

urlpatterns = [
    path('flight-arrivals/', views.FlightArrivalListCreateView.as_view(), name='flight-arrival-list-create'),
    path('flight-arrivals/<int:pk>/', views.FlightArrivalDetailView.as_view(), name='flight-arrival-detail'),
]
