"""pressing/admin.py — Administration E-Shelle Pressing"""
from datetime import date, timedelta
from django.contrib import admin
from django.utils.html import format_html
from .models import (VillePressing, QuartierPressing, CategoriePressing,
                     Pressing, ServicePressing, CommandePressing, AvisPressing)


@admin.register(VillePressing)
class VillePressingAdmin(admin.ModelAdmin):
    list_display  = ("nom", "region", "nb_pressings", "active", "ordre")
    list_editable = ("active", "ordre")
    list_display_links = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}

    @admin.display(description="Pressings")
    def nb_pressings(self, obj):
        n = obj.pressings.filter(is_active=True).count()
        return format_html('<strong style="color:#6366F1">{}</strong>', n)


@admin.register(QuartierPressing)
class QuartierPressingAdmin(admin.ModelAdmin):
    list_display  = ("nom", "ville", "active")
    list_filter   = ("ville", "active")
    search_fields = ("nom",)
    list_editable = ("active",)
    list_display_links = ("nom",)


@admin.register(CategoriePressing)
class CategoriePressingAdmin(admin.ModelAdmin):
    list_display  = ("icone", "nom", "slug", "active", "ordre")
    list_editable = ("active", "ordre")
    list_display_links = ("nom",)
    prepopulated_fields = {"slug": ("nom",)}


class ServiceInline(admin.TabularInline):
    model = ServicePressing
    extra = 1
    fields = ("categorie", "icone", "nom", "prix", "unite", "disponible", "ordre")


class AvisInline(admin.TabularInline):
    model = AvisPressing
    extra = 0
    readonly_fields = ("auteur", "note", "commentaire", "created_at")
    can_delete = False


@admin.register(Pressing)
class PressingAdmin(admin.ModelAdmin):
    list_display = (
        "photo_preview", "nom", "ville",
        "telephone_link", "abonnement_badge", "statut_badge",
        "express_badge", "note_badge", "is_featured", "created_at",
    )
    list_filter   = ("ville", "is_active", "abonnement_actif", "plan_actif",
                     "is_verified", "is_featured", "express",
                     "collecte_domicile", "livraison_domicile")
    search_fields = ("nom", "telephone", "whatsapp", "adresse", "ref_paiement")
    list_editable = ("is_featured",)
    list_display_links = ("nom",)
    filter_horizontal = ("categories",)
    date_hierarchy = "created_at"
    ordering = ("-abonnement_actif", "-is_featured", "-created_at")
    inlines = [ServiceInline, AvisInline]
    prepopulated_fields = {"slug": ("nom",)}
    readonly_fields = ("note_moyenne", "nb_avis", "nb_vues", "created_at", "updated_at")
    actions = ["activer_1mois", "activer_3mois", "suspendre"]

    fieldsets = (
        ("IDENTITÉ", {
            "fields": ("nom", "slug", "description", "photo", "logo", "gerant"),
        }),
        ("LOCALISATION", {
            "fields": ("ville", "quartier", "adresse", "zone_livraison"),
        }),
        ("CONTACT", {
            "fields": ("telephone", "whatsapp", "whatsapp_msg"),
        }),
        ("SERVICES", {
            "fields": ("categories", "horaires", "collecte_domicile", "livraison_domicile",
                       "delai_traitement", "delai_livraison", "express"),
        }),
        ("SOUSCRIPTION MENSUELLE", {
            "fields": ("plan_actif", "abonnement_actif", "abonnement_expire_le",
                       "montant_paye", "ref_paiement", "notes_admin"),
            "description": "Basic 2000 FCFA | Pro 5000 FCFA | Premium 10000 FCFA / mois.",
        }),
        ("VISIBILITÉ", {
            "fields": ("is_active", "is_verified", "is_featured"),
        }),
        ("STATS (lecture seule)", {
            "fields": ("note_moyenne", "nb_avis", "nb_vues"),
            "classes": ("collapse",),
        }),
    )

    @admin.action(description="Activer abonnement 1 mois")
    def activer_1mois(self, request, queryset):
        expire = date.today() + timedelta(days=30)
        n = queryset.update(abonnement_actif=True, is_active=True, abonnement_expire_le=expire)
        self.message_user(request, f"{n} pressing(s) activé(s) jusqu'au {expire}.")

    @admin.action(description="Activer abonnement 3 mois")
    def activer_3mois(self, request, queryset):
        expire = date.today() + timedelta(days=90)
        n = queryset.update(abonnement_actif=True, is_active=True, abonnement_expire_le=expire)
        self.message_user(request, f"{n} pressing(s) activé(s) jusqu'au {expire}.")

    @admin.action(description="Suspendre l'abonnement")
    def suspendre(self, request, queryset):
        n = queryset.update(abonnement_actif=False, is_active=False)
        self.message_user(request, f"{n} pressing(s) suspendu(s).")

    @admin.display(description="Photo")
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="40" style="object-fit:cover;border-radius:8px"/>',
                obj.photo.url
            )
        return format_html(
            '<div style="width:50px;height:40px;background:linear-gradient(135deg,#6366F1,#4F46E5);'
            'border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.3rem">&#128085;</div>'
        )

    @admin.display(description="Téléphone")
    def telephone_link(self, obj):
        return format_html(
            '<a href="tel:{}" style="font-weight:700;color:#6366F1">{}</a>',
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

    @admin.display(description="Express")
    def express_badge(self, obj):
        if obj.express:
            return format_html('<span style="background:#ede9fe;color:#7c3aed;padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">⚡ Express</span>')
        return "—"

    @admin.display(description="Note")
    def note_badge(self, obj):
        if obj.nb_avis == 0:
            return "—"
        stars = "★" * obj.etoiles + "☆" * (5 - obj.etoiles)
        return format_html(
            '<span style="color:#6366F1;font-size:.85rem" title="{} avis">{}</span>',
            obj.nb_avis, stars
        )


@admin.register(ServicePressing)
class ServicePressingAdmin(admin.ModelAdmin):
    list_display  = ("nom", "pressing", "categorie", "prix_fcfa", "unite", "disponible", "ordre")
    list_filter   = ("disponible", "categorie", "pressing__ville")
    search_fields = ("nom", "pressing__nom")
    list_editable = ("disponible", "ordre")
    list_display_links = ("nom",)
    ordering = ("pressing", "categorie", "ordre")

    @admin.display(description="Prix")
    def prix_fcfa(self, obj):
        return format_html('<strong style="color:#6366F1">{} FCFA</strong>', obj.prix)


@admin.register(CommandePressing)
class CommandePressingAdmin(admin.ModelAdmin):
    list_display  = ("id", "pressing", "client_nom", "statut_badge",
                     "mode", "montant_total_display", "created_at")
    list_filter   = ("statut", "mode", "pressing__ville", "pressing")
    search_fields = ("pressing__nom", "nom_client", "tel_client", "adresse_collecte")
    readonly_fields = ("created_at", "updated_at", "whatsapp_link")
    list_display_links = ("id",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        ("COMMANDE", {
            "fields": ("pressing", "client", "nom_client", "tel_client"),
        }),
        ("DÉTAILS", {
            "fields": ("mode", "adresse_collecte", "articles", "notes",
                       "montant_total", "statut"),
        }),
        ("DATES", {
            "fields": ("date_collecte", "date_pret"),
        }),
        ("ACTIONS", {
            "fields": ("whatsapp_link", "created_at", "updated_at"),
        }),
    )

    @admin.display(description="Statut")
    def statut_badge(self, obj):
        colors = {
            "en_attente": ("#854d0e", "#fef9c3"),
            "confirme":   ("#1e40af", "#dbeafe"),
            "en_cours":   ("#3730a3", "#ede9fe"),
            "pret":       ("#15803d", "#dcfce7"),
            "livre":      ("#374151", "#f3f4f6"),
            "annule":     ("#991b1b", "#fee2e2"),
        }
        color, bg = colors.get(obj.statut, ("#374151", "#f3f4f6"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:12px;font-size:.75rem;font-weight:700">{}</span>',
            bg, color, obj.get_statut_display()
        )

    @admin.display(description="Total")
    def montant_total_display(self, obj):
        return format_html('<strong style="color:#6366F1">{} FCFA</strong>', obj.montant_total)

    @admin.display(description="WhatsApp")
    def whatsapp_link(self, obj):
        url = obj.whatsapp_recap_url()
        return format_html(
            '<a href="{}" target="_blank" style="background:#25D366;color:#fff;padding:4px 12px;border-radius:8px;font-weight:700;font-size:.8rem">Envoyer récap WhatsApp</a>',
            url
        )


@admin.register(AvisPressing)
class AvisPressingAdmin(admin.ModelAdmin):
    list_display  = ("pressing", "auteur", "note", "commentaire_court", "created_at")
    list_filter   = ("note", "pressing__ville")
    search_fields = ("pressing__nom", "auteur__username", "commentaire")
    readonly_fields = ("created_at",)

    @admin.display(description="Commentaire")
    def commentaire_court(self, obj):
        return obj.commentaire[:60] + "..." if len(obj.commentaire) > 60 else obj.commentaire
