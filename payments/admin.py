from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction, Coupon


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ("reference", "utilisateur", "type_tx", "methode",
                      "montant_affiche", "statut_display", "created_at")
    list_filter   = ("statut", "methode", "type_tx")
    search_fields = ("reference", "utilisateur__username", "telephone", "ref_operateur")
    readonly_fields = ("reference", "created_at", "updated_at")
    date_hierarchy = "created_at"

    def montant_affiche(self, obj):
        return f"{int(obj.montant):,} {obj.devise}".replace(",", " ")
    montant_affiche.short_description = "Montant"

    def statut_display(self, obj):
        colors = {
            "succes":     "#4CAF50",
            "echec":      "#EF5350",
            "rembourse":  "#FF9800",
            "en_attente": "#FFB74D",
            "initie":     "#9E9E9E",
            "expire":     "#616161",
        }
        return format_html('<span style="color:{};font-weight:600">{}</span>',
                           colors.get(obj.statut, "#fff"), obj.get_statut_display())
    statut_display.short_description = "Statut"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display  = ("code", "type_coupon", "valeur", "nb_utilisations",
                      "max_utilisations", "est_valide_display", "actif")
    list_filter   = ("type_coupon", "actif")
    search_fields = ("code",)
    list_editable = ("actif",)

    def est_valide_display(self, obj):
        if obj.est_valide:
            return format_html('<span style="color:#4CAF50">✓ Valide</span>')
        return format_html('<span style="color:#EF5350">✗ Invalide</span>')
    est_valide_display.short_description = "Validité"
