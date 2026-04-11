"""gaz/admin.py — Administration E-Shelle Gaz"""
from django.contrib import admin
from django.utils.html import format_html
from .models import VilleGaz, QuartierGaz, MarqueGaz, DepotGaz, AvisDepot


@admin.register(VilleGaz)
class VilleGazAdmin(admin.ModelAdmin):
    list_display  = ("nom", "region", "nb_depots", "active", "ordre")
    list_editable = ("active", "ordre")
    list_display_links = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}
    ordering = ["ordre", "nom"]

    @admin.display(description="Depots")
    def nb_depots(self, obj):
        n = obj.depots.filter(is_active=True).count()
        return format_html('<strong style="color:#FF6B00">{}</strong>', n)


@admin.register(QuartierGaz)
class QuartierGazAdmin(admin.ModelAdmin):
    list_display  = ("nom", "ville", "active")
    list_filter   = ("ville", "active")
    search_fields = ("nom",)
    list_editable = ("active",)
    list_display_links = ("nom",)


@admin.register(MarqueGaz)
class MarqueGazAdmin(admin.ModelAdmin):
    list_display  = ("nom_badge", "slug", "active")
    list_editable = ("active",)
    list_display_links = ("nom_badge",)
    prepopulated_fields = {"slug": ("nom",)}

    @admin.display(description="Marque")
    def nom_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-weight:700">{}</span>',
            obj.couleur, obj.nom
        )


class AvisDepotInline(admin.TabularInline):
    model = AvisDepot
    extra = 0
    readonly_fields = ("auteur", "note", "commentaire", "created_at")
    can_delete = False


@admin.register(DepotGaz)
class DepotGazAdmin(admin.ModelAdmin):
    list_display = (
        "photo_preview", "nom", "ville", "quartier",
        "telephone_link", "statut_badge", "note_badge",
        "is_featured", "is_verified", "created_at",
    )
    list_filter   = ("ville", "is_active", "is_verified", "is_featured", "livraison_rapide", "livraison_nuit")
    search_fields = ("nom", "telephone", "whatsapp", "adresse", "zone_livraison")
    list_editable = ("is_featured", "is_verified")
    list_display_links = ("nom",)
    filter_horizontal = ("marques",)
    date_hierarchy = "created_at"
    ordering = ("-is_featured", "-created_at")
    inlines = [AvisDepotInline]

    fieldsets = (
        ("IDENTITE DU DEPOT", {
            "fields": ("nom", "slug", "description", "photo", "gerant"),
        }),
        ("LOCALISATION", {
            "fields": ("ville", "quartier", "adresse", "zone_livraison"),
        }),
        ("CONTACT", {
            "fields": ("telephone", "whatsapp", "whatsapp_msg"),
            "description": "Le numero WhatsApp doit etre sans + (ex: 237680625082)"
        }),
        ("PRODUITS DISPONIBLES", {
            "fields": ("marques", "tailles", "prix_6kg", "prix_12kg", "prix_15kg"),
        }),
        ("SERVICE & HORAIRES", {
            "fields": ("livraison_rapide", "delai_livraison", "horaires",
                       "livraison_nuit", "paiement_info"),
        }),
        ("VISIBILITE", {
            "fields": ("is_active", "is_verified", "is_featured"),
        }),
        ("STATISTIQUES (lecture seule)", {
            "fields": ("note_moyenne", "nb_avis"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("note_moyenne", "nb_avis", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("nom",)}

    @admin.display(description="Photo")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="40" style="object-fit:cover;border-radius:8px"/>',
                obj.photo.url
            )
        return format_html(
            '<div style="width:50px;height:40px;background:linear-gradient(135deg,#FF6B00,#FFD700);'
            'border-radius:8px;display:flex;align-items:center;justify-content:center;'
            'font-size:1.4rem">&#128293;</div>'
        )

    @admin.display(description="Telephone")
    def telephone_link(self, obj):
        return format_html(
            '<a href="tel:{}" style="font-weight:700;color:#FF6B00">{}</a>',
            obj.telephone, obj.telephone
        )

    @admin.display(description="Statut")
    def statut_badge(self, obj):
        if not obj.is_active:
            return format_html('<span style="background:#f3f4f6;color:#6b7280;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">Inactif</span>')
        if obj.is_verified:
            return format_html('<span style="background:#dcfce7;color:#15803d;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">Verifie</span>')
        return format_html('<span style="background:#fef9c3;color:#854d0e;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">En attente</span>')

    @admin.display(description="Note")
    def note_badge(self, obj):
        if obj.nb_avis == 0:
            return "—"
        stars = "★" * obj.etoiles + "☆" * (5 - obj.etoiles)
        return format_html(
            '<span style="color:#FF6B00;font-size:.85rem" title="{} avis">{}</span>',
            obj.nb_avis, stars
        )


@admin.register(AvisDepot)
class AvisDepotAdmin(admin.ModelAdmin):
    list_display  = ("depot", "auteur", "note", "commentaire_court", "created_at")
    list_filter   = ("note", "depot__ville")
    search_fields = ("depot__nom", "auteur__username", "commentaire")
    readonly_fields = ("created_at",)

    @admin.display(description="Commentaire")
    def commentaire_court(self, obj):
        return obj.commentaire[:60] + "..." if len(obj.commentaire) > 60 else obj.commentaire
