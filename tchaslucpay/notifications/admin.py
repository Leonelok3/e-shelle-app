from django.contrib import admin

from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Journal des notifications SMS et email generees par Tchaslucpay."""

    list_display = ("channel", "recipient", "status", "user", "created_at", "sent_at")
    list_filter = ("channel", "status", "created_at")
    search_fields = ("recipient", "subject", "message", "user__username")
    readonly_fields = ("created_at", "sent_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
