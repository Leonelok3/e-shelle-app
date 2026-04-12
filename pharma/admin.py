"""pharma/admin.py — Administration E-Shelle Pharma"""
from datetime import date, timedelta
from django.contrib import admin
from django.utils.html import format_html
from .models import (VillePharma, QuartierPharma, CategorieMedicament,
                     Medicament, Pharmacie, StockPharmacie, AvisPharmacie)


@admin.register(VillePharma)
class VillePharmaAdmin(admin.ModelAdmin):
    list_display  = ("nom", "region", "nb_pharmacies", "active", "ordre")
    list_editable = ("active", "ordre")
    list_display_links = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}
    ordering = ["ordre", "nom"]

    @admin.display(description="Pharmacies")
    def nb_pharmacies(self, obj):
        n = obj.pharmacies.filter(is_active=True).count()
        return format_html('<strong style="color:#10B981">{}</strong>', n)


@admin.register(QuartierPharma)
class QuartierPharmaAdmin(admin.ModelAdmin):
    list_display  = ("nom", "ville", "active")
    list_filter   = ("ville", "active")
    search_fields = ("nom",)
    list_editable = ("active",)
    list_display_links = ("nom",)


@admin.register(CategorieMedicament)
class CategorieMedicamentAdmin(admin.ModelAdmin):
    list_display  = ("icone", "nom", "slug", "active", "ordre")
    list_editable = ("active", "ordre")
    list_display_links = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}


class StockInline(admin.TabularInline):
    model = StockPharmacie
    extra = 0
    fields = ("medicament", "prix", "disponible")
    autocomplete_fields = ("medicament",)


class AvisPharmaInline(admin.TabularInline):
    model = AvisPharmacie
    extra = 0
    readonly_fields = ("auteur", "note", "commentaire", "created_at")
    can_delete = False


@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display  = ("nom", "categorie", "ordonnance_badge", "nb_pharma_dispo", "actif")
    list_filter   = ("categorie", "ordonnance", "actif")
    search_fields = ("nom", "description")
    list_editable = ("actif",)
    list_display_links = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}

    @admin.display(description="Ordonnance")
    def ordonnance_badge(self, obj):
        if obj.ordonnance:
            return format_html(
                '<span style="background:#fef2f2;color:#dc2626;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">Ordo</span>'
            )
        return format_html(
            '<span style="background:#f0fdf4;color:#16a34a;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">Libre</span>'
        )

    @admin.display(description="Dispo dans")
    def nb_pharma_dispo(self, obj):
        n = obj.stocks.filter(disponible=True, pharmacie__is_active=True).count()
        color = "#10B981" if n > 0 else "#6b7280"
        return format_html('<strong style="color:{}">{} pharmacie(s)</strong>', color, n)


@admin.register(Pharmacie)
class PharmacieAdmin(admin.ModelAdmin):
    list_display = (
        "photo_preview", "nom", "ville",
        "telephone_link", "abonnement_badge", "statut_badge",
        "garde_badge", "note_badge", "is_featured", "created_at",
    )
    list_filter   = ("ville", "is_active", "abonnement_actif", "plan_actif",
                     "is_verified", "is_featured", "garde", "livraison")
    search_fields = ("nom", "telephone", "whatsapp", "adresse", "ref_paiement")
    list_editable = ("is_featured",)
    list_display_links = ("nom",)
    date_hierarchy = "created_at"
    ordering = ("-abonnement_actif", "-is_featured", "-created_at")
    inlines = [StockInline, AvisPharmaInline]

    fieldsets = (
        ("IDENTITÉ DE LA PHARMACIE", {
            "fields": ("nom", "slug", "description", "photo", "gerant"),
        }),
        ("LOCALISATION", {
            "fields": ("ville", "quartier", "adresse"),
        }),
        ("CONTACT", {
            "fields": ("telephone", "whatsapp", "whatsapp_msg"),
            "description": "Le numéro WhatsApp doit être sans + (ex: 237680625082)"
        }),
        ("SERVICE & HORAIRES", {
            "fields": ("horaires", "garde", "garde_info", "livraison", "delai_livraison"),
        }),
        ("SOUSCRIPTION MENSUELLE", {
            "fields": (
                "plan_actif", "abonnement_actif", "abonnement_expire_le",
                "montant_paye", "ref_paiement", "notes_admin",
            ),
            "description": (
                "Activez l'abonnement après réception du paiement (Orange Money / MTN). "
                "Basic 2000 FCFA | Pro 5000 FCFA | Premium 10000 FCFA / mois."
            ),
        }),
        ("VISIBILITÉ", {
            "fields": ("is_active", "is_verified", "is_featured"),
        }),
        ("STATISTIQUES (lecture seule)", {
            "fields": ("note_moyenne", "nb_avis"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("note_moyenne", "nb_avis", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("nom",)}
    actions = ["activer_1mois", "activer_3mois", "suspendre"]

    @admin.action(description="Activer abonnement 1 mois")
    def activer_1mois(self, request, queryset):
        expire = date.today() + timedelta(days=30)
        n = queryset.update(abonnement_actif=True, is_active=True, abonnement_expire_le=expire)
        self.message_user(request, f"{n} pharmacie(s) activée(s) jusqu'au {expire}.")

    @admin.action(description="Activer abonnement 3 mois")
    def activer_3mois(self, request, queryset):
        expire = date.today() + timedelta(days=90)
        n = queryset.update(abonnement_actif=True, is_active=True, abonnement_expire_le=expire)
        self.message_user(request, f"{n} pharmacie(s) activée(s) jusqu'au {expire}.")

    @admin.action(description="Suspendre l'abonnement")
    def suspendre(self, request, queryset):
        n = queryset.update(abonnement_actif=False, is_active=False)
        self.message_user(request, f"{n} pharmacie(s) suspendue(s).")

    @admin.display(description="Photo")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="40" style="object-fit:cover;border-radius:8px"/>',
                obj.photo.url
            )
        return format_html(
            '<div style="width:50px;height:40px;background:linear-gradient(135deg,#10B981,#059669);'
            'border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.3rem">&#128138;</div>'
        )

    @admin.display(description="Téléphone")
    def telephone_link(self, obj):
        return format_html(
            '<a href="tel:{}" style="font-weight:700;color:#10B981">{}</a>',
            obj.telephone, obj.telephone
        )

    @admin.display(description="Abonnement")
    def abonnement_badge(self, obj):
        if not obj.abonnement_actif:
            return format_html(
                '<span style="background:#f3f4f6;color:#6b7280;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">Inactif</span>'
            )
        jr = obj.jours_restants
        color, bg = ("#15803d", "#dcfce7") if jr > 15 else (("#9a3412", "#fff7ed") if jr > 5 else ("#854d0e", "#fef9c3"))
        plan = obj.get_plan_actif_display() or "Actif"
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">{} — {}j</span>',
            bg, color, plan, jr
        )

    @admin.display(description="Statut")
    def statut_badge(self, obj):
        if not obj.is_active:
            return format_html('<span style="background:#f3f4f6;color:#6b7280;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">Inactif</span>')
        if obj.is_verified:
            return format_html('<span style="background:#dcfce7;color:#15803d;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">Vérifié</span>')
        return format_html('<span style="background:#fef9c3;color:#854d0e;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">En attente</span>')

    @admin.display(description="Garde")
    def garde_badge(self, obj):
        if obj.garde:
            return format_html('<span style="background:#ede9fe;color:#7c3aed;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">🌙 Garde</span>')
        return "—"

    @admin.display(description="Note")
    def note_badge(self, obj):
        if obj.nb_avis == 0:
            return "—"
        stars = "★" * obj.etoiles + "☆" * (5 - obj.etoiles)
        return format_html(
            '<span style="color:#10B981;font-size:.85rem" title="{} avis">{}</span>',
            obj.nb_avis, stars
        )


@admin.register(StockPharmacie)
class StockPharmacieAdmin(admin.ModelAdmin):
    list_display  = ("medicament", "pharmacie", "prix_display", "disponible", "updated_at")
    list_filter   = ("disponible", "pharmacie__ville", "medicament__categorie")
    search_fields = ("medicament__nom", "pharmacie__nom")
    list_editable = ("disponible",)
    list_display_links = ("medicament",)
    autocomplete_fields = ("medicament", "pharmacie")

    @admin.display(description="Prix")
    def prix_display(self, obj):
        if obj.prix:
            return format_html('<strong style="color:#10B981">{} FCFA</strong>', obj.prix)
        return format_html('<span style="color:#9ca3af">N/C</span>')


@admin.register(AvisPharmacie)
class AvisPharmacieAdmin(admin.ModelAdmin):
    list_display  = ("pharmacie", "auteur", "note", "commentaire_court", "created_at")
    list_filter   = ("note", "pharmacie__ville")
    search_fields = ("pharmacie__nom", "auteur__username", "commentaire")
    readonly_fields = ("created_at",)

    @admin.display(description="Commentaire")
    def commentaire_court(self, obj):
        return obj.commentaire[:60] + "..." if len(obj.commentaire) > 60 else obj.commentaire
