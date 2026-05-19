from django.contrib import admin
from django.utils.html import format_html

from .models import DemandeTrajet, Trajet, VilleTransport


@admin.register(VilleTransport)
class VilleTransportAdmin(admin.ModelAdmin):
    list_display = ("nom", "region", "active", "ordre")
    list_editable = ("active", "ordre")
    prepopulated_fields = {"slug": ("nom",)}
    search_fields = ("nom", "region")


@admin.register(Trajet)
class TrajetAdmin(admin.ModelAdmin):
    list_display = ("trajet", "type_trajet", "date_depart", "heure_depart", "prix_place", "places_disponibles", "statut_badge", "is_featured")
    list_filter = ("type_trajet", "statut", "is_active", "is_verified", "is_featured", "depart", "arrivee")
    list_editable = ("is_featured",)
    search_fields = ("titre", "conducteur_nom", "telephone", "depart__nom", "arrivee__nom")
    prepopulated_fields = {"slug": ("titre",)}
    date_hierarchy = "date_depart"
    actions = ["publier", "marquer_complet"]

    @admin.display(description="Trajet")
    def trajet(self, obj):
        return f"{obj.depart} -> {obj.arrivee}"

    @admin.display(description="Statut")
    def statut_badge(self, obj):
        if obj.is_active and obj.is_verified and obj.statut == Trajet.Statut.OUVERT:
            return format_html('<span style="background:#dcfce7;color:#166534;padding:3px 8px;border-radius:999px;font-weight:700">Ouvert</span>')
        if obj.statut == Trajet.Statut.COMPLET:
            return format_html('<span style="background:#dbeafe;color:#1d4ed8;padding:3px 8px;border-radius:999px;font-weight:700">Complet</span>')
        return format_html('<span style="background:#f3f4f6;color:#6b7280;padding:3px 8px;border-radius:999px;font-weight:700">A verifier</span>')

    @admin.action(description="Publier et verifier")
    def publier(self, request, queryset):
        updated = queryset.update(is_active=True, is_verified=True, statut=Trajet.Statut.OUVERT)
        self.message_user(request, f"{updated} trajet(s) publie(s).")

    @admin.action(description="Marquer complet")
    def marquer_complet(self, request, queryset):
        updated = queryset.update(statut=Trajet.Statut.COMPLET)
        self.message_user(request, f"{updated} trajet(s) complet(s).")


@admin.register(DemandeTrajet)
class DemandeTrajetAdmin(admin.ModelAdmin):
    list_display = ("nom", "depart", "arrivee", "date_souhaitee", "places", "telephone", "is_active")
    list_filter = ("is_active", "depart", "arrivee", "date_souhaitee")
    search_fields = ("nom", "telephone", "depart__nom", "arrivee__nom")
    list_editable = ("is_active",)
