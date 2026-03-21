"""api/urls.py — Endpoints REST E-Shelle"""
from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path("search/",              views.search,              name="search"),
    path("notifications/count/", views.notifications_count, name="notif_count"),
]
