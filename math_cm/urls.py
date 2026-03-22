from django.urls import path
from . import views

app_name = 'math_cm'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('classes/', views.choisir_classe, name='choisir_classe'),
    path('classe/<str:classe_nom>/', views.liste_chapitres, name='liste_chapitres'),
    path('chapitre/<slug:slug>/', views.detail_chapitre, name='detail_chapitre'),
    path('chapitre/<slug:chap_slug>/lecon/<slug:lecon_slug>/', views.cours_detail, name='cours_detail'),
    path('chapitre/<slug:chap_slug>/lecon/<slug:lecon_slug>/complete/', views.marquer_complete, name='marquer_complete'),
    path('exercice/<int:pk>/', views.exercice_detail, name='exercice_detail'),
    path('exercice/<int:pk>/soumettre/', views.soumettre_exercice, name='soumettre_exercice'),
    path('exercice/<int:pk>/correction/', views.voir_correction, name='voir_correction'),
    path('chapitre/<slug:slug>/quiz/', views.quiz_chapitre, name='quiz_chapitre'),
    path('examens/', views.liste_epreuves, name='liste_epreuves'),
    path('examen/<slug:slug>/', views.examen_detail, name='examen_detail'),
    path('examen/<slug:slug>/passer/', views.passer_examen, name='passer_examen'),
    path('examen/<slug:slug>/resultat/<int:resultat_id>/', views.resultat_epreuve, name='resultat_epreuve'),
    path('ma-progression/', views.progression_eleve, name='progression_eleve'),
    path('api/progression/', views.api_progression, name='api_progression'),
    path('api/stats-chapitre/<slug:slug>/', views.api_stats_chapitre, name='api_stats_chapitre'),
]
