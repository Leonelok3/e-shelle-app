"""pressing/urls.py — E-Shelle Pressing"""
from django.urls import path
from . import views

app_name = "pressing"

urlpatterns = [
    path("",                          views.accueil,        name="accueil"),
    path("etablissements/",           views.catalogue,      name="catalogue"),
    path("p/<slug:slug>/",            views.detail,         name="detail"),
    path("p/<slug:slug>/commander/",  views.commander,      name="commander"),
    path("confirmation/<int:pk>/",    views.confirmation,   name="confirmation"),
    path("dashboard/",                views.dashboard,      name="dashboard"),
    path("commande/<int:pk>/statut/", views.update_statut,  name="update_statut"),
]
