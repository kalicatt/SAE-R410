from django.urls import path
from .views import index, destinations, signup_view, signup_success, login_view, login_success, profile_view, flight_detail
from .views import admin_dashboard, reservations, payment, bank_payment
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path('destinations/', destinations, name='destinations'),
    path('signup/', signup_view, name='signup'),
    path('signup/success/', signup_success, name='signup_success'),
    path('login/', login_view, name='login'),
    path('login/success/', login_success, name='login_success'),
    path('profile/', profile_view, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('flights/<str:flight_type>/<int:flight_id>/', flight_detail, name='flight_detail'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('reservations/', reservations, name='reservations'),
    path('payment/', payment, name='payment'),
    
    path('bank_payment/', bank_payment, name='bank_payment'),
]