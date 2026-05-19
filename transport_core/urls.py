from django.urls import path
from . import views

app_name = "transport"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("trajets/", views.catalogue, name="catalogue"),
    path("publier/", views.publier, name="publier"),
    path("demande/", views.demande, name="demande"),
    path("trajet/<slug:slug>/", views.detail, name="detail"),
]
