"""payments/urls.py"""
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("payer/<int:commande_id>/",     views.initier,       name="initier"),
    path("confirmation/<int:tx_id>/",    views.confirmation,  name="confirmation"),
    path("historique/",                  views.historique,    name="historique"),
    path("webhook/",                     views.webhook,       name="webhook"),
]
