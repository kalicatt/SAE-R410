from django.urls import path, include
from rest_framework import viewsets
from .views import ClientApiView

urlpatterns = [

    path('client/', ClientApiView.as_view()),
]