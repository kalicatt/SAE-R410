# Aeroport_project/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('API-client/', include('client_app.urls')),
    path('API-reservation/', include('reservation_app.urls')),
    path('API-depart/', include('vols_depart_app.urls')),  # Inclure les URLs des départs
    path('API-arriver/', include('vols_arriver_app.urls')),   # Inclure les URLs des arrivées
    path('API-staff/', include('staff_app.urls')),
    path('API-paiement/', include('paiement_app.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('API-token-auth/', obtain_auth_token, name='api_token_auth'),
]