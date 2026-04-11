"""
E-Shelle Resto — Administration Django
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    City, Neighborhood, FoodCategory, Restaurant,
    Subscription, MenuCategory, Dish, ContactLog, Favorite,
    HeroBanner, Review, Notification,
)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["is_active"]


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "slug"]
    list_filter = ["city"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ["icon", "name", "slug", "order"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ("name",)}


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "status", "is_approved", "is_featured", "is_active", "views_count", "created_at"]
    list_filter = ["status", "is_approved", "is_featured", "is_active", "city"]
    list_editable = ["is_approved", "is_featured", "is_active"]
    search_fields = ["name", "owner__email", "phone"]
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ["owner"]
    inlines = [SubscriptionInline]
    actions = ["approve_restaurants", "feature_restaurants", "unapprove_restaurants"]

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px">', obj.cover_image.url)
        return "—"
    cover_preview.short_description = "Photo"

    @admin.action(description="✅ Approuver les restaurants sélectionnés")
    def approve_restaurants(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} restaurant(s) approuvé(s).")

    @admin.action(description="⭐ Mettre en avant les restaurants sélectionnés")
    def feature_restaurants(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} restaurant(s) mis en avant.")

    @admin.action(description="❌ Désapprouver les restaurants sélectionnés")
    def unapprove_restaurants(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} restaurant(s) désapprouvé(s).")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["restaurant", "plan", "is_active", "start_date", "expiry_date", "days_remaining_display"]
    list_filter = ["plan", "is_active"]
    raw_id_fields = ["restaurant"]

    def days_remaining_display(self, obj):
        days = obj.days_remaining
        color = "green" if days > 7 else "red"
        return format_html('<span style="color:{}">{} jours</span>', color, days)
    days_remaining_display.short_description = "Jours restants"


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "restaurant", "order"]
    list_filter = ["restaurant"]
    list_editable = ["order"]


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ["name", "restaurant", "category", "formatted_price_display", "availability", "is_popular", "is_active"]
    list_filter = ["availability", "is_popular", "is_active", "restaurant__city"]
    list_editable = ["availability", "is_active"]
    search_fields = ["name", "restaurant__name"]
    raw_id_fields = ["restaurant", "category"]

    def formatted_price_display(self, obj):
        return obj.formatted_price
    formatted_price_display.short_description = "Prix"


@admin.register(ContactLog)
class ContactLogAdmin(admin.ModelAdmin):
    list_display = ["restaurant", "action", "dish", "ip_address", "created_at"]
    list_filter = ["action", "restaurant__city"]
    readonly_fields = ["restaurant", "action", "dish", "session_key", "ip_address", "user_agent", "created_at"]
    date_hierarchy = "created_at"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "restaurant", "created_at"]
    raw_id_fields = ["user", "restaurant"]


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = [
        "order", "preview_thumbnail", "title", "media_type",
        "tag", "restaurant", "duration", "is_active",
    ]
    list_display_links = ["title", "preview_thumbnail"]
    list_editable = ["order", "is_active"]
    list_filter = ["media_type", "tag", "is_active"]
    search_fields = ["title", "subtitle", "restaurant__name"]
    raw_id_fields = ["restaurant"]
    ordering = ["order"]

    fieldsets = (
        ("Contenu", {
            "fields": ("title", "subtitle", "tag"),
        }),
        ("Média", {
            "fields": ("media_type", "image", "video", "video_poster"),
            "description": "Uploadez une image OU une vidéo selon le type choisi.",
        }),
        ("Bouton d'action (CTA)", {
            "fields": ("cta_label", "cta_url", "restaurant"),
            "description": (
                "Si un restaurant est sélectionné, le bouton pointera automatiquement "
                "vers sa page — inutile de renseigner l'URL manuellement."
            ),
        }),
        ("Paramètres d'affichage", {
            "fields": ("duration", "order", "is_active"),
        }),
    )

    def preview_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px;width:80px;object-fit:cover;'
                'border-radius:6px;" />',
                obj.image.url,
            )
        if obj.video_poster:
            return format_html(
                '<img src="{}" style="height:48px;width:80px;object-fit:cover;'
                'border-radius:6px;border:2px solid #6366f1;" />',
                obj.video_poster.url,
            )
        if obj.video:
            return format_html(
                '<span style="display:inline-flex;align-items:center;gap:4px;'
                'padding:4px 8px;background:#1e293b;color:white;border-radius:6px;'
                'font-size:11px;">▶ Vidéo</span>'
            )
        return "—"
    preview_thumbnail.short_description = "Aperçu"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ["author_name", "restaurant", "stars_display", "is_approved", "created_at"]
    list_filter   = ["is_approved", "rating", "restaurant__city"]
    list_editable = ["is_approved"]
    search_fields = ["author_name", "comment", "restaurant__name"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
    actions = ["approve_reviews"]

    def stars_display(self, obj):
        full  = "★" * obj.rating
        empty = "☆" * (5 - obj.rating)
        color = "#f59e0b" if obj.rating >= 4 else "#94a3b8"
        return format_html(
            '<span style="color:{};font-size:16px;">{}</span>'
            '<span style="color:#cbd5e1;font-size:16px;">{}</span>',
            color, full, empty,
        )
    stars_display.short_description = "Note"

    @admin.action(description="✅ Approuver les avis sélectionnés")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} avis approuvé(s).")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ["restaurant", "type", "short_message", "is_read", "created_at"]
    list_filter   = ["type", "is_read"]
    list_editable = ["is_read"]
    date_hierarchy = "created_at"

    def short_message(self, obj):
        return obj.message[:80] + ("…" if len(obj.message) > 80 else "")
    short_message.short_description = "Message"
