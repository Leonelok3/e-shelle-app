"""
admin.py — auto_cameroun
Interface d'administration pour le marketplace automobile Cameroun
"""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import (
    ProfilAuto, Vehicule, PhotoVehicule,
    DemandeEssai, FavorisVehicule, SignalementVehicule,
    DemandeSoumissionVehicule, StatutVehicule,
)


# ─────────────────────────────────────────────────────────────────
# INLINES
# ─────────────────────────────────────────────────────────────────

class PhotoVehiculeInline(admin.TabularInline):
    model    = PhotoVehicule
    extra    = 3
    fields   = ["image", "legende", "est_photo_principale", "ordre", "apercu"]
    readonly_fields = ["apercu"]

    def apercu(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return "—"
    apercu.short_description = "Aperçu"


# ─────────────────────────────────────────────────────────────────
# VÉHICULE ADMIN
# ─────────────────────────────────────────────────────────────────

@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = [
        "titre_avec_badge", "marque", "modele", "annee",
        "type_transaction", "ville", "prix_formate_display",
        "statut_badge", "est_mis_en_avant", "est_coup_de_coeur",
        "proprietaire", "vues", "created_at",
    ]
    list_filter  = [
        "statut", "type_carrosserie", "type_transaction", "carburant",
        "boite", "ville", "est_mis_en_avant", "est_coup_de_coeur",
        "est_dedouane", "publie_par_admin",
    ]
    search_fields = [
        "titre", "marque", "modele", "ville", "quartier",
        "proprietaire__email", "proprietaire__username",
    ]
    list_editable   = ["est_mis_en_avant", "est_coup_de_coeur"]
    readonly_fields = ["vues", "created_at", "updated_at", "date_publication", "apercu_photo_principale"]
    prepopulated_fields = {"slug": ("titre",)}
    inlines      = [PhotoVehiculeInline]
    date_hierarchy = "created_at"
    ordering     = ["-created_at"]

    fieldsets = (
        ("🚗 Identité", {
            "fields": ("titre", "slug", "marque", "modele", "annee", "version", "couleur", "immatriculation"),
        }),
        ("📋 Classification", {
            "fields": ("type_transaction", "type_carrosserie", "etat"),
        }),
        ("⚙️ Motorisation", {
            "fields": ("carburant", "boite", "puissance_cv", "cylindree", "conduite"),
        }),
        ("📊 Données", {
            "fields": ("kilometrage", "nombre_places", "nombre_portes"),
        }),
        ("📍 Localisation", {
            "fields": ("ville", "quartier", "adresse_complete"),
        }),
        ("💰 Tarification", {
            "fields": ("prix", "devise", "periode_prix", "prix_negociable", "date_disponibilite"),
        }),
        ("📝 Description", {
            "fields": ("description", "options_equipements"),
        }),
        ("✅ Garanties", {
            "fields": ("est_dedouane", "garantie", "premiere_main"),
        }),
        ("🚀 Publication", {
            "fields": ("statut", "est_mis_en_avant", "est_coup_de_coeur", "publie_par_admin", "proprietaire", "note_admin"),
        }),
        ("🔍 SEO", {
            "fields": ("meta_description", "meta_keywords"),
            "classes": ("collapse",),
        }),
        ("📊 Stats", {
            "fields": ("vues", "created_at", "updated_at", "date_publication", "apercu_photo_principale"),
            "classes": ("collapse",),
        }),
    )

    actions = [
        "action_publier", "action_mettre_en_avant",
        "action_marquer_reserve", "action_archiver", "action_coup_de_coeur",
    ]

    @admin.action(description="✅ Publier les véhicules sélectionnés")
    def action_publier(self, request, queryset):
        count = queryset.update(
            statut=StatutVehicule.PUBLIE,
            publie_par_admin=True,
            date_publication=timezone.now(),
        )
        self.message_user(request, f"{count} véhicule(s) publié(s).")

    @admin.action(description="⭐ Mettre en avant (Premium)")
    def action_mettre_en_avant(self, request, queryset):
        count = queryset.update(est_mis_en_avant=True)
        self.message_user(request, f"{count} véhicule(s) mis en avant.")

    @admin.action(description="🔒 Marquer comme Réservé")
    def action_marquer_reserve(self, request, queryset):
        count = queryset.update(statut=StatutVehicule.RESERVE)
        self.message_user(request, f"{count} véhicule(s) marqué(s) Réservé.")

    @admin.action(description="📦 Archiver les véhicules sélectionnés")
    def action_archiver(self, request, queryset):
        count = queryset.update(statut=StatutVehicule.ARCHIVE)
        self.message_user(request, f"{count} véhicule(s) archivé(s).")

    @admin.action(description="❤️ Marquer comme Coup de cœur")
    def action_coup_de_coeur(self, request, queryset):
        count = queryset.update(est_coup_de_coeur=True)
        self.message_user(request, f"{count} véhicule(s) marqué(s) Coup de cœur.")

    def save_model(self, request, obj, form, change):
        if obj.statut == StatutVehicule.PUBLIE:
            obj.publie_par_admin = True
            if not obj.date_publication:
                obj.date_publication = timezone.now()
        super().save_model(request, obj, form, change)

    def titre_avec_badge(self, obj):
        badges = ""
        if obj.est_coup_de_coeur:
            badges += ' <span style="background:#F4A261;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;">❤️ Coup de cœur</span>'
        if obj.est_mis_en_avant:
            badges += ' <span style="background:#1B4332;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;">⭐ En avant</span>'
        return format_html("{}{}", obj.titre, mark_safe(badges))
    titre_avec_badge.short_description = "Titre"

    def prix_formate_display(self, obj):
        return obj.prix_formate
    prix_formate_display.short_description = "Prix"

    STATUT_COULEURS = {
        "PUBLIE":                ("#1B4332", "#fff"),
        "EN_ATTENTE_VALIDATION": ("#F4A261", "#fff"),
        "RESERVE":               ("#457B9D", "#fff"),
        "VENDU_LOUE":            ("#6c757d", "#fff"),
        "REFUSE":                ("#e63946", "#fff"),
        "ARCHIVE":               ("#adb5bd", "#333"),
        "BROUILLON":             ("#dee2e6", "#333"),
    }

    def statut_badge(self, obj):
        bg, fg = self.STATUT_COULEURS.get(obj.statut, ("#dee2e6", "#333"))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            bg, fg, obj.get_statut_display()
        )
    statut_badge.short_description = "Statut"

    def apercu_photo_principale(self, obj):
        photo = obj.photo_principale
        if photo and photo.image:
            return format_html(
                '<img src="{}" style="max-width:300px;border-radius:8px;" />',
                photo.image.url
            )
        return "Aucune photo"
    apercu_photo_principale.short_description = "Aperçu"


# ─────────────────────────────────────────────────────────────────
# PROFIL AUTO ADMIN
# ─────────────────────────────────────────────────────────────────

@admin.register(ProfilAuto)
class ProfilAutoAdmin(admin.ModelAdmin):
    list_display  = ["user", "role", "compte_type", "ville", "est_verifie", "date_expiration_premium", "created_at"]
    list_filter   = ["role", "compte_type", "est_verifie"]
    list_editable = ["compte_type", "est_verifie"]
    search_fields = ["user__username", "user__email", "telephone", "ville"]
    readonly_fields = ["created_at", "updated_at"]


# ─────────────────────────────────────────────────────────────────
# DEMANDE D'ESSAI ADMIN
# ─────────────────────────────────────────────────────────────────

@admin.register(DemandeEssai)
class DemandeEssaiAdmin(admin.ModelAdmin):
    list_display  = ["nom_complet", "telephone", "vehicule", "date_souhaitee", "statut", "created_at"]
    list_filter   = ["statut", "created_at"]
    search_fields = ["nom_complet", "telephone", "email", "vehicule__titre"]
    list_editable = ["statut"]
    readonly_fields = ["created_at"]
    actions = ["action_confirmer", "action_annuler"]

    @admin.action(description="✅ Confirmer les essais sélectionnés")
    def action_confirmer(self, request, queryset):
        queryset.update(statut="CONFIRME")
        self.message_user(request, "Essais confirmés.")

    @admin.action(description="❌ Annuler les essais sélectionnés")
    def action_annuler(self, request, queryset):
        queryset.update(statut="ANNULE")
        self.message_user(request, "Essais annulés.")


# ─────────────────────────────────────────────────────────────────
# SIGNALEMENT ADMIN
# ─────────────────────────────────────────────────────────────────

@admin.register(SignalementVehicule)
class SignalementVehiculeAdmin(admin.ModelAdmin):
    list_display  = ["vehicule", "motif", "user", "traite", "created_at"]
    list_filter   = ["motif", "traite"]
    list_editable = ["traite"]
    readonly_fields = ["created_at"]


# ─────────────────────────────────────────────────────────────────
# SOUMISSION ADMIN
# ─────────────────────────────────────────────────────────────────

@admin.register(DemandeSoumissionVehicule)
class DemandeSoumissionVehiculeAdmin(admin.ModelAdmin):
    list_display  = ["nom_complet", "telephone", "marque", "modele", "annee", "ville", "statut_badge_soumission", "created_at"]
    list_filter   = ["statut", "type_transaction", "ville"]
    search_fields = ["nom_complet", "telephone", "email", "marque", "modele", "ville"]
    readonly_fields = ["created_at"]
    actions = ["action_creer_vehicule", "action_rejeter"]

    STATUT_COULEURS = {
        "RECU":          ("#F4A261", "#fff"),
        "EN_TRAITEMENT": ("#457B9D", "#fff"),
        "PUBLIE":        ("#1B4332", "#fff"),
        "REJETE":        ("#e63946", "#fff"),
    }

    def statut_badge_soumission(self, obj):
        bg, fg = self.STATUT_COULEURS.get(obj.statut, ("#dee2e6", "#333"))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            bg, fg, obj.get_statut_display()
        )
    statut_badge_soumission.short_description = "Statut"

    @admin.action(description="🚗 Créer un véhicule à partir de cette soumission")
    def action_creer_vehicule(self, request, queryset):
        soumission = queryset.first()
        if not soumission:
            return
        queryset.update(statut="EN_TRAITEMENT")
        url = (
            reverse("admin:auto_cameroun_vehicule_add")
            + f"?marque={soumission.marque}"
            + f"&modele={soumission.modele}"
            + f"&annee={soumission.annee}"
            + f"&ville={soumission.ville}"
        )
        return HttpResponseRedirect(url)

    @admin.action(description="❌ Rejeter les soumissions sélectionnées")
    def action_rejeter(self, request, queryset):
        queryset.update(statut="REJETE")
        self.message_user(request, "Soumissions rejetées.")


# ─────────────────────────────────────────────────────────────────
# FAVORIS ADMIN
# ─────────────────────────────────────────────────────────────────

@admin.register(FavorisVehicule)
class FavorisVehiculeAdmin(admin.ModelAdmin):
    list_display  = ["user", "vehicule", "created_at"]
    readonly_fields = ["user", "vehicule", "created_at"]
    list_filter  = ["created_at"]
