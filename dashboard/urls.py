"""dashboard/urls.py"""
from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("",                 views.index,         name="index"),
    path("notifications/",   views.notifications, name="notifications"),
]
