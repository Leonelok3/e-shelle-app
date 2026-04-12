"""pharma/urls.py — E-Shelle Pharma"""
from django.urls import path
from . import views

app_name = "pharma"

urlpatterns = [
    path("",                              views.accueil,            name="accueil"),
    path("medicaments/",                  views.recherche,          name="recherche"),
    path("medicament/<slug:slug>/",       views.detail_medicament,  name="detail_medicament"),
    path("pharmacies/",                   views.catalogue,          name="catalogue"),
    path("pharmacie/<slug:slug>/",        views.detail_pharmacie,   name="detail_pharmacie"),
]
