"""boutique/urls.py"""
from django.urls import path
from . import views

app_name = "boutique"

urlpatterns = [
    path("",                              views.index,            name="index"),
    path("catalogue/",                    views.catalogue,        name="catalogue"),
    path("panier/",                       views.voir_panier,      name="panier"),
    path("panier/ajouter/<int:produit_id>/", views.ajouter_au_panier, name="ajouter"),
    path("panier/retirer/<int:ligne_id>/",   views.retirer_du_panier, name="retirer"),
    path("checkout/",                     views.checkout,         name="checkout"),
    path("telecharger/<uuid:token>/",     views.telecharger,      name="telecharger"),
    path("<slug:slug>/",                  views.detail_produit,   name="detail"),
]
