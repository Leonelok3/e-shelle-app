from django.contrib import admin
from django.utils.html import format_html
from .models import GenerationIA, TemplatePrompt


@admin.register(GenerationIA)
class GenerationIAAdmin(admin.ModelAdmin):
    list_display  = ("utilisateur", "type_gen", "modele", "tokens_total_display",
                      "statut_display", "sauvegarde", "created_at")
    list_filter   = ("type_gen", "statut", "sauvegarde", "modele")
    search_fields = ("utilisateur__username", "prompt", "resultat")
    readonly_fields = ("created_at", "tokens_input", "tokens_output", "duree_ms")
    date_hierarchy = "created_at"

    def tokens_total_display(self, obj):
        return f"{obj.tokens_total:,}"
    tokens_total_display.short_description = "Tokens"

    def statut_display(self, obj):
        colors = {"succes": "#4CAF50", "erreur": "#EF5350", "en_cours": "#FFB74D"}
        return format_html('<span style="color:{}">{}</span>',
                           colors.get(obj.statut, "#fff"), obj.get_statut_display())
    statut_display.short_description = "Statut"


@admin.register(TemplatePrompt)
class TemplatePromptAdmin(admin.ModelAdmin):
    list_display  = ("nom", "type_gen", "actif", "created_at")
    list_filter   = ("type_gen", "actif")
    search_fields = ("nom", "template")
    list_editable = ("actif",)
