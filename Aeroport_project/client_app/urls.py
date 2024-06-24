

from django.urls import path
from .views import ClientApiView, ClientDetailApiView

urlpatterns = [
    path('clients/', ClientApiView.as_view(), name='client-list'),
    path('clients/<int:pk>/', ClientDetailApiView.as_view(), name='client-detail'),
]