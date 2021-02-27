from django.urls import path, include
from django.contrib import admin
from .views import index, room

urlpatterns = [
    path('', index, name="index"),
    path('<str:room_name>/', room, name='room'),
]
