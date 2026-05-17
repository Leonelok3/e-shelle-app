from django.contrib import admin

from .models import AccountBalance, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Lecture et controle des ecritures financieres Tchaslucpay."""

    list_display = (
        "trid",
        "account",
        "collector",
        "transaction_type",
        "status",
        "amount",
        "balance_before",
        "balance_after",
        "created_at",
    )
    list_filter = ("transaction_type", "status", "created_at")
    search_fields = ("trid", "account__username", "collector__username", "description")
    autocomplete_fields = ("account", "collector", "created_by", "reversed_transaction")
    readonly_fields = ("trid", "created_at", "posted_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(AccountBalance)
class AccountBalanceAdmin(admin.ModelAdmin):
    """Vue technique des soldes associes aux utilisateurs."""

    list_display = ("user", "available_balance", "locked_balance", "currency", "updated_at")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    readonly_fields = ("updated_at",)
