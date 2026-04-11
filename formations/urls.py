"""formations/urls.py"""
from django.urls import path
from . import views

app_name = "formations"

urlpatterns = [
    path("",                                              views.catalogue,     name="catalogue"),
    path("mon-espace/",                                   views.mon_dashboard, name="mon_dashboard"),
    path("<slug:slug>/",                                  views.detail,        name="detail"),
    path("<slug:slug>/inscrire/",                         views.inscrire,      name="inscrire"),
    path("<slug:formation_slug>/lecon/<int:lecon_id>/",   views.lecteur,       name="lecteur"),
]
