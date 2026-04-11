"""services/urls.py"""
from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path("",                views.index,         name="index"),
    path("portfolio/",      views.portfolio,     name="portfolio"),
    path("configurateur/",  views.configurateur, name="configurateur"),
    path("contact/",        views.contact,       name="contact"),
    path("devis/",          views.devis,         name="devis"),
]
