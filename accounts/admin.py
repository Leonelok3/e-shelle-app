from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    CustomUser, UserProfile, StudentProfile,
    AppPlan, AppSubscription, PaymentHistory,
)


# ─── Utilisateurs ────────────────────────────────────────────────

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ("username", "email", "role", "is_staff", "is_active", "date_joined")
    list_filter   = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (
        ("Rôle E-Shelle", {"fields": ("role",)}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "level", "plan", "pays", "created_at")
    search_fields = ("user__username", "user__email")
    list_filter   = ("plan", "level")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "class_level")
    search_fields = ("user__username",)


# ─── Plans d'application ─────────────────────────────────────────

@admin.register(AppPlan)
class AppPlanAdmin(admin.ModelAdmin):
    list_display  = ("name", "app_key", "level", "price_xaf_badge", "duration_days", "is_free", "is_popular", "is_active", "order")
    list_filter   = ("app_key", "level", "is_free", "is_popular", "is_active")
    search_fields = ("name", "slug")
    list_editable = ("order", "is_active", "is_popular")
    list_display_links = ("name",)
    prepopulated_fields = {"slug": ("app_key", "name")}
    ordering = ("app_key", "order")

    fieldsets = (
        ("Identité", {
            "fields": ("app_key", "slug", "name", "level", "description")
        }),
        ("Tarification", {
            "fields": ("price_xaf", "price_eur", "duration_days", "is_free")
        }),
        ("Fonctionnalités", {
            "fields": ("features",)
        }),
        ("Affichage", {
            "fields": ("is_popular", "is_active", "order")
        }),
    )

    @admin.display(description="Prix")
    def price_xaf_badge(self, obj):
        if obj.price_xaf == 0:
            return format_html('<span style="color:#10b981;font-weight:bold">Gratuit</span>')
        return format_html('<strong>{} FCFA</strong>', f"{obj.price_xaf:,}".replace(",", " "))


# ─── Abonnements ─────────────────────────────────────────────────

@admin.register(AppSubscription)
class AppSubscriptionAdmin(admin.ModelAdmin):
    list_display  = ("user", "plan", "status_badge", "started_at", "expires_at", "days_remaining_display", "auto_renew")
    list_filter   = ("status", "plan__app_key", "plan__level", "auto_renew")
    search_fields = ("user__username", "user__email", "plan__name", "payment_ref")
    raw_id_fields = ("user",)
    list_display_links = ("user",)
    date_hierarchy = "started_at"
    ordering = ("-started_at",)

    fieldsets = (
        ("Utilisateur & Plan", {
            "fields": ("user", "plan", "status")
        }),
        ("Dates", {
            "fields": ("started_at", "expires_at", "auto_renew")
        }),
        ("Paiement", {
            "fields": ("payment_ref", "notes")
        }),
    )
    readonly_fields = ("started_at",)

    @admin.display(description="Statut")
    def status_badge(self, obj):
        colors = {
            "active":    "#10b981",
            "trial":     "#3b82f6",
            "expired":   "#ef4444",
            "cancelled": "#6b7280",
            "pending":   "#f59e0b",
        }
        color = colors.get(obj.status, "#6b7280")
        label = obj.get_status_display()
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:.78rem;font-weight:600">{}</span>',
            color, label
        )

    @admin.display(description="Jours restants")
    def days_remaining_display(self, obj):
        r = obj.days_remaining
        if r is None:
            return "∞ Illimité"
        if r == 0:
            return format_html('<span style="color:#ef4444">Expiré</span>')
        if r <= 7:
            return format_html('<span style="color:#f59e0b">{} j</span>', r)
        return f"{r} j"


# ─── Historique paiements ────────────────────────────────────────

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display  = ("user", "amount_badge", "method", "status_badge", "description_short", "created_at")
    list_filter   = ("status", "method")
    search_fields = ("user__username", "user__email", "reference", "description")
    raw_id_fields = ("user",)
    list_display_links = ("user",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    @admin.display(description="Montant")
    def amount_badge(self, obj):
        if obj.amount_xaf == 0:
            return format_html('<span style="color:#10b981">Gratuit</span>')
        return format_html('<strong>{}</strong>', obj.amount_formatted)

    @admin.display(description="Statut")
    def status_badge(self, obj):
        colors = {"pending": "#f59e0b", "success": "#10b981", "failed": "#ef4444", "refunded": "#8b5cf6"}
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:.78rem;font-weight:600">{}</span>',
            color, obj.get_status_display()
        )

    @admin.display(description="Description")
    def description_short(self, obj):
        return obj.description[:60] + "…" if len(obj.description) > 60 else obj.description
