"""
admin.py — annonces_cam
Interface d'administration pour la marketplace généraliste Cameroun
"""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Categorie, ProfilVendeur, Annonce, PhotoAnnonce,
    BoostAnnonce, FavoriAnnonce, SignalementAnnonce,
    ConversationAnnonce, MessageAnnonce, AvisVendeur,
    StatutAnnonce,
)


# ─────────────────────────────────────────────────────────────────
# INLINES
# ─────────────────────────────────────────────────────────────────

class PhotoAnnonceInline(admin.TabularInline):
    model   = PhotoAnnonce
    extra   = 3
    fields  = ["image", "legende", "est_photo_principale", "ordre", "apercu"]
    readonly_fields = ["apercu"]

    def apercu(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return "—"
    apercu.short_description = "Aperçu"


class BoostAnnonceInline(admin.TabularInline):
    model   = BoostAnnonce
    extra   = 0
    fields  = ["type_boost", "prix_paye", "date_fin", "est_actif"]
    readonly_fields = ["date_debut"]


# ─────────────────────────────────────────────────────────────────
# CATÉGORIE
# ─────────────────────────────────────────────────────────────────

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display   = ["nom", "parent", "icone", "couleur_hex", "ordre", "est_active", "est_vedette", "nombre_annonces"]
    list_filter    = ["est_active", "est_vedette", "parent"]
    list_editable  = ["ordre", "est_active", "est_vedette"]
    search_fields  = ["nom", "description"]
    prepopulated_fields = {"slug": ("nom",)}
    readonly_fields = ["nombre_annonces", "created_at"]

    fieldsets = (
        ("Informations", {
            "fields": ("nom", "slug", "parent", "description", "image_banniere"),
        }),
        ("Apparence", {
            "fields": ("icone", "couleur_hex"),
        }),
        ("Options", {
            "fields": ("ordre", "est_active", "est_vedette"),
        }),
        ("Stats", {
            "fields": ("nombre_annonces", "created_at"),
            "classes": ("collapse",),
        }),
    )


# ─────────────────────────────────────────────────────────────────
# ANNONCE
# ─────────────────────────────────────────────────────────────────

STATUT_COULEURS = {
    "PUBLIEE":               ("#1B4332", "#fff"),
    "EN_ATTENTE_VALIDATION": ("#F4A261", "#fff"),
    "VENDUE":                ("#6c757d", "#fff"),
    "EXPIREE":               ("#adb5bd", "#333"),
    "REFUSEE":               ("#e63946", "#fff"),
    "ARCHIVEE":              ("#dee2e6", "#333"),
    "BROUILLON":             ("#dee2e6", "#333"),
    "SUSPENDUE":             ("#457B9D", "#fff"),
}


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display  = [
        "titre_avec_badge", "categorie", "ville",
        "prix_formate_display", "statut_badge",
        "est_mise_en_avant", "est_urgente", "est_coup_de_coeur",
        "vendeur", "vues", "created_at",
    ]
    list_filter   = [
        "statut", "categorie", "ville",
        "est_mise_en_avant", "est_urgente", "est_coup_de_coeur",
        "etat_produit", "devise",
    ]
    search_fields = [
        "titre", "description", "ville", "quartier",
        "vendeur__email", "vendeur__username",
    ]
    list_editable   = ["est_mise_en_avant", "est_urgente", "est_coup_de_coeur"]
    readonly_fields = ["vues", "nombre_contacts", "nombre_favoris", "created_at", "updated_at", "date_publication", "apercu_photo_principale"]
    prepopulated_fields = {"slug": ("titre",)}
    inlines      = [PhotoAnnonceInline, BoostAnnonceInline]
    date_hierarchy = "created_at"
    ordering     = ["-created_at"]

    fieldsets = (
        ("📋 Annonce", {
            "fields": ("titre", "slug", "categorie", "description", "etat_produit"),
        }),
        ("💰 Prix", {
            "fields": ("prix", "devise", "prix_a_debattre", "gratuit"),
        }),
        ("📍 Localisation", {
            "fields": ("ville", "quartier", "adresse_precise", "latitude", "longitude"),
        }),
        ("📞 Contact", {
            "fields": ("telephone_contact", "whatsapp_contact", "email_contact", "mode_contact"),
        }),
        ("🚀 Publication", {
            "fields": (
                "statut", "est_mise_en_avant", "est_urgente", "est_coup_de_coeur",
                "publie_par_admin", "vendeur", "note_admin", "date_expiration",
            ),
        }),
        ("🔍 SEO", {
            "fields": ("meta_description",),
            "classes": ("collapse",),
        }),
        ("📊 Stats", {
            "fields": ("vues", "nombre_contacts", "nombre_favoris", "created_at", "updated_at", "date_publication", "apercu_photo_principale"),
            "classes": ("collapse",),
        }),
    )

    actions = [
        "action_publier", "action_mettre_en_avant",
        "action_urgente", "action_archiver", "action_coup_de_coeur",
    ]

    @admin.action(description="✅ Publier les annonces sélectionnées")
    def action_publier(self, request, queryset):
        from django.utils import timezone as tz
        from datetime import timedelta
        count = queryset.update(
            statut=StatutAnnonce.PUBLIEE,
            publie_par_admin=True,
            date_publication=tz.now(),
            date_expiration=(tz.now() + timedelta(days=30)).date(),
        )
        self.message_user(request, f"{count} annonce(s) publiée(s).")

    @admin.action(description="⭐ Mettre en avant")
    def action_mettre_en_avant(self, request, queryset):
        count = queryset.update(est_mise_en_avant=True)
        self.message_user(request, f"{count} annonce(s) mise(s) en avant.")

    @admin.action(description="🔥 Marquer Urgent")
    def action_urgente(self, request, queryset):
        count = queryset.update(est_urgente=True)
        self.message_user(request, f"{count} annonce(s) marquée(s) Urgent.")

    @admin.action(description="📦 Archiver")
    def action_archiver(self, request, queryset):
        count = queryset.update(statut=StatutAnnonce.ARCHIVEE)
        self.message_user(request, f"{count} annonce(s) archivée(s).")

    @admin.action(description="❤️ Coup de cœur")
    def action_coup_de_coeur(self, request, queryset):
        count = queryset.update(est_coup_de_coeur=True)
        self.message_user(request, f"{count} annonce(s) marquée(s) Coup de cœur.")

    def save_model(self, request, obj, form, change):
        if obj.statut == StatutAnnonce.PUBLIEE:
            obj.publie_par_admin = True
            if not obj.date_publication:
                obj.date_publication = timezone.now()
            if not obj.date_expiration:
                from datetime import timedelta
                obj.date_expiration = (timezone.now() + timedelta(days=30)).date()
        super().save_model(request, obj, form, change)

    def titre_avec_badge(self, obj):
        badges = ""
        if obj.est_coup_de_coeur:
            badges += ' <span style="background:#F4A261;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;">❤️</span>'
        if obj.est_mise_en_avant:
            badges += ' <span style="background:#1B4332;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;">⭐</span>'
        if obj.est_urgente:
            badges += ' <span style="background:#e63946;color:#fff;padding:2px 6px;border-radius:4px;font-size:11px;">🔥 Urgent</span>'
        return format_html("{}{}", obj.titre, mark_safe(badges))
    titre_avec_badge.short_description = "Titre"

    def prix_formate_display(self, obj):
        return obj.prix_formate
    prix_formate_display.short_description = "Prix"

    def statut_badge(self, obj):
        bg, fg = STATUT_COULEURS.get(obj.statut, ("#dee2e6", "#333"))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            bg, fg, obj.get_statut_display()
        )
    statut_badge.short_description = "Statut"

    def apercu_photo_principale(self, obj):
        photo = obj.photo_principale
        if photo and photo.image:
            return format_html('<img src="{}" style="max-width:300px;border-radius:8px;" />', photo.image.url)
        return "Aucune photo"
    apercu_photo_principale.short_description = "Aperçu"


# ─────────────────────────────────────────────────────────────────
# PROFIL VENDEUR
# ─────────────────────────────────────────────────────────────────

@admin.register(ProfilVendeur)
class ProfilVendeurAdmin(admin.ModelAdmin):
    list_display  = ["user", "nom_boutique", "compte_type", "ville", "est_verifie", "note_moyenne", "nombre_ventes_reussies", "created_at"]
    list_filter   = ["compte_type", "est_verifie"]
    list_editable = ["compte_type", "est_verifie"]
    search_fields = ["user__username", "user__email", "telephone", "ville", "nom_boutique"]
    readonly_fields = ["created_at", "updated_at", "note_moyenne", "nombre_avis", "nombre_ventes_reussies"]


# ─────────────────────────────────────────────────────────────────
# SIGNALEMENT
# ─────────────────────────────────────────────────────────────────

@admin.register(SignalementAnnonce)
class SignalementAnnonceAdmin(admin.ModelAdmin):
    list_display  = ["annonce", "motif", "user", "traite", "created_at"]
    list_filter   = ["motif", "traite"]
    list_editable = ["traite"]
    readonly_fields = ["created_at"]
    search_fields = ["annonce__titre", "description"]


# ─────────────────────────────────────────────────────────────────
# AVIS VENDEUR
# ─────────────────────────────────────────────────────────────────

@admin.register(AvisVendeur)
class AvisVendeurAdmin(admin.ModelAdmin):
    list_display  = ["vendeur", "acheteur", "note", "annonce", "created_at"]
    list_filter   = ["note", "created_at"]
    readonly_fields = ["created_at"]
    search_fields = ["vendeur__username", "acheteur__username"]


# ─────────────────────────────────────────────────────────────────
# CONVERSATION / MESSAGES
# ─────────────────────────────────────────────────────────────────

class MessageAnnonceInline(admin.TabularInline):
    model   = MessageAnnonce
    extra   = 0
    fields  = ["expediteur", "destinataire", "contenu", "lu", "created_at"]
    readonly_fields = ["expediteur", "destinataire", "contenu", "lu", "created_at"]


@admin.register(ConversationAnnonce)
class ConversationAnnonceAdmin(admin.ModelAdmin):
    list_display  = ["annonce", "acheteur", "vendeur", "derniere_activite"]
    readonly_fields = ["created_at", "derniere_activite"]
    inlines = [MessageAnnonceInline]


# ─────────────────────────────────────────────────────────────────
# FAVORIS
# ─────────────────────────────────────────────────────────────────

@admin.register(FavoriAnnonce)
class FavoriAnnonceAdmin(admin.ModelAdmin):
    list_display  = ["user", "annonce", "created_at"]
    readonly_fields = ["user", "annonce", "created_at"]
