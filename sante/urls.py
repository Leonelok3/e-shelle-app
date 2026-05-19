from django.urls import path

from . import views

app_name = "sante"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("produits/", views.produits, name="produits"),
    path("produits/publier/", views.publier_produit, name="publier_produit"),
    path("produit/<slug:slug>/", views.detail_produit, name="detail_produit"),
    path("urgence/", views.urgence, name="urgence"),
    path("espace-vendeur/", views.espace_vendeur, name="espace_vendeur"),
    path("professionnels/", views.professionnels, name="professionnels"),
    path("professionnels/inscrire/", views.inscrire_professionnel, name="inscrire_professionnel"),
    path("professionnel/<slug:slug>/", views.detail_professionnel, name="detail_professionnel"),
    path("professionnel/<slug:slug>/rendez-vous/", views.prendre_rendez_vous, name="rendez_vous"),
    path("demande/", views.demande, name="demande"),
]
