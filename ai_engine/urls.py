"""ai_engine/urls.py"""
from django.urls import path
from . import views

app_name = "ai_engine"

urlpatterns = [
    path("",          views.generateur,     name="generateur"),
    path("stream/",   views.stream_generate, name="stream"),
    path("historique/", views.historique_ia, name="historique"),
]
