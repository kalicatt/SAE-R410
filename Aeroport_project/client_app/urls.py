from django.urls import path
from .views import ClientApiView
from .views import ClientDetailApiView

urlpatterns = [
    path('signup/', ClientApiView.as_view(), name='api_client'),
    path('client/', ClientApiView.as_view()),
    path('client/<int:pk>/', ClientDetailApiView.as_view(), name='client-detail'),
]