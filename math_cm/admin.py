from django.contrib import admin
from .models import (
    Classe, Chapitre, Lecon, Exercice, EpreuveExamen,
    ProfilEleve, ProgressionLecon, ResultatExercice, ResultatEpreuve, Badge
)


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ['label', 'nom', 'examen_fin_annee', 'ordre', 'is_active']
    list_editable = ['ordre', 'is_active']
    ordering = ['ordre']


@admin.register(Chapitre)
class ChapitreAdmin(admin.ModelAdmin):
    list_display = ['classe', 'numero', 'titre', 'categorie', 'difficulte', 'is_published', 'is_premium']
    list_filter = ['classe', 'categorie', 'difficulte', 'is_published', 'is_premium']
    list_editable = ['is_published', 'is_premium']
    search_fields = ['titre']
    prepopulated_fields = {'slug': ('titre',)}
    ordering = ['classe', 'numero']


@admin.register(Lecon)
class LeconAdmin(admin.ModelAdmin):
    list_display = ['chapitre', 'ordre', 'titre', 'type_lecon', 'duree_lecture', 'is_free', 'is_published']
    list_filter = ['chapitre__classe', 'type_lecon', 'is_free', 'is_published']
    list_editable = ['is_published', 'is_free']
    search_fields = ['titre', 'chapitre__titre']
    ordering = ['chapitre', 'ordre']


@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    list_display = ['chapitre', 'numero', 'titre', 'type_exercice', 'niveau', 'bareme', 'is_published']
    list_filter = ['chapitre__classe', 'type_exercice', 'niveau', 'is_published']
    list_editable = ['is_published']
    search_fields = ['titre', 'chapitre__titre']


@admin.register(EpreuveExamen)
class EpreuveExamenAdmin(admin.ModelAdmin):
    list_display = ['titre', 'classe', 'type_examen', 'serie', 'annee', 'duree', 'is_premium', 'is_published']
    list_filter = ['classe', 'type_examen', 'serie', 'is_premium', 'is_published']
    list_editable = ['is_published', 'is_premium']
    prepopulated_fields = {'slug': ('titre',)}


@admin.register(ProfilEleve)
class ProfilEleveAdmin(admin.ModelAdmin):
    list_display = ['user', 'classe', 'ville', 'points_total', 'streak_jours', 'niveau_badge']
    list_filter = ['classe', 'ville']
    search_fields = ['user__username', 'user__first_name', 'etablissement']
    readonly_fields = ['points_total', 'streak_jours', 'niveau_badge']


@admin.register(ResultatEpreuve)
class ResultatEpreuveAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'epreuve', 'note', 'date_passage']
    list_filter = ['epreuve__classe', 'epreuve__type_examen']
    readonly_fields = ['date_passage']


admin.site.register(ProgressionLecon)
admin.site.register(ResultatExercice)
admin.site.register(Badge)
