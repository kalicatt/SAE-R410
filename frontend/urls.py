from django.urls import path, os
from .views import index, about, offers, seats, destinations, login, signup_view, signup_success

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('offers/', offers, name='offers'),
    path('seats/', seats, name='seats'),
    path('destinations/', destinations, name='destinations'),
    path('login/', login, name='login'),
    path('signup/', signup_view, name='signup'),
    path('signup/success/', signup_success, name='signup_success'),
]
