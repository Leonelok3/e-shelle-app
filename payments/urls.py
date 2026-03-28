"""payments/urls.py"""
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("payer/<int:commande_id>/",     views.initier,       name="initier"),
    path("confirmation/<int:tx_id>/",    views.confirmation,  name="confirmation"),
    path("historique/",                  views.historique,    name="historique"),
    path("webhook/",                     views.webhook,       name="webhook"),
    path("formation/<int:formation_id>/", views.payer_formation, name="payer_formation"),

    # Packs Premium Marketplace
    path("premium/<str:module>/",                    views.premium_marketplace, name="premium_marketplace"),
    path("premium/<str:module>/<str:plan_slug>/",    views.payer_premium,       name="payer_premium"),
    path("premium/confirmation/<int:tx_id>/",        views.confirmation_premium, name="confirmation_premium"),

    # Boost annonce individuelle
    path("boost/annonce/<int:annonce_id>/<str:type_boost>/", views.booster_annonce, name="booster_annonce"),
]
