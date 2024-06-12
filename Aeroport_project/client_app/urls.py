from django.urls import path
from .views import ClientApiView
from .views import ClientDetailApiView

urlpatterns = [

    path('client/', ClientApiView.as_view()),
    path('client/<int:pk>/', ClientDetailApiView.as_view(), name='client-detail'),
]