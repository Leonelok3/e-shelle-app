"""
Njangi+ — Administration Django
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Group, Membership,
    Session, Contribution,
    FundDeposit, FundTransaction,
    Loan, LoanRepayment,
    Notification, Document,
)


# ── Groupe & Membres ──────────────────────────────────────────────────────────

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    fields = ("user", "role", "hand_order", "is_active", "total_contributed", "total_received")
    readonly_fields = ("total_contributed", "total_received")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display  = ("name", "status", "member_count", "frequency", "contribution_amount", "current_cycle", "created_at")
    list_filter   = ("status", "frequency")
    search_fields = ("name", "invite_code")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("fund_balance", "fund_available_for_loans", "invite_code")
    inlines = [MembershipInline]

    fieldsets = (
        ("Identité", {"fields": ("name", "slug", "invite_code", "description", "logo", "created_by")}),
        ("Configuration", {"fields": (
            "frequency", "contribution_amount", "max_members",
            "fund_loan_rate", "fund_deposit_rate", "penalty_per_day",
            "max_loan_multiplier", "fund_reserve_pct", "require_guarantor",
        )}),
        ("Calendrier", {"fields": ("start_date", "next_session_date", "current_cycle")}),
        ("État", {"fields": ("status",)}),
        ("Fond commun (calculé)", {"fields": ("fund_balance", "fund_available_for_loans"), "classes": ("collapse",)}),
    )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display  = ("user", "group", "role", "hand_order", "is_active", "total_contributed", "total_received")
    list_filter   = ("role", "is_active", "group")
    search_fields = ("user__username", "user__email", "group__name")
    raw_id_fields = ("user", "group")


# ── Séances & Cotisations ─────────────────────────────────────────────────────

class ContributionInline(admin.TabularInline):
    model = Contribution
    extra = 0
    fields = ("membership", "amount_due", "amount_paid", "status", "payment_method", "paid_at")
    readonly_fields = ("paid_at",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display  = ("__str__", "date", "status", "total_collected", "hand_amount", "attendance_rate")
    list_filter   = ("status", "group", "cycle")
    search_fields = ("group__name",)
    readonly_fields = ("total_collected", "hand_amount", "penalties_collected", "opened_at", "closed_at", "attendance_rate")
    inlines = [ContributionInline]


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display  = ("membership", "session", "amount_due", "amount_paid", "status", "is_late", "paid_at")
    list_filter   = ("status", "is_late", "payment_method")
    search_fields = ("membership__user__username", "transaction_ref")
    readonly_fields = ("paid_at",)


# ── Fond commun ───────────────────────────────────────────────────────────────

@admin.register(FundDeposit)
class FundDepositAdmin(admin.ModelAdmin):
    list_display  = ("membership", "amount", "interest_rate", "duration_months", "status", "deposited_at", "maturity_date")
    list_filter   = ("status",)
    search_fields = ("membership__user__username",)
    readonly_fields = ("deposited_at", "interest_earned", "withdrawn_at", "withdrawn_amount", "current_interest", "expected_interest")


@admin.register(FundTransaction)
class FundTransactionAdmin(admin.ModelAdmin):
    list_display  = ("group", "type", "amount", "signed_amount", "balance_after", "created_at", "is_credit_badge")
    list_filter   = ("type", "group")
    search_fields = ("description", "group__name")
    readonly_fields = ("signed_amount", "created_at")

    def is_credit_badge(self, obj):
        color = "green" if obj.is_credit else "red"
        label = "+" if obj.is_credit else "−"
        return format_html('<span style="color:{};font-weight:bold">{}</span>', color, label)
    is_credit_badge.short_description = "Sens"


# ── Prêts ─────────────────────────────────────────────────────────────────────

class LoanRepaymentInline(admin.TabularInline):
    model = LoanRepayment
    extra = 0
    fields = ("amount_paid", "principal_part", "interest_part", "balance_after", "payment_method", "paid_at")
    readonly_fields = ("principal_part", "interest_part", "balance_after", "paid_at")


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display  = ("membership", "amount_approved", "interest_rate", "duration_months", "status", "due_date", "repayment_progress_pct")
    list_filter   = ("status",)
    search_fields = ("membership__user__username",)
    readonly_fields = ("requested_at", "approved_at", "disbursed_at", "total_interest", "total_due", "total_repaid", "balance_remaining", "repayment_progress_pct")
    inlines = [LoanRepaymentInline]

    fieldsets = (
        ("Demande", {"fields": ("membership", "guarantor", "amount_requested", "purpose", "requested_at")}),
        ("Décision", {"fields": ("status", "amount_approved", "interest_rate", "duration_months", "reviewed_by", "approved_at", "rejection_reason")}),
        ("Décaissement", {"fields": ("disbursed_at", "due_date", "payment_method", "transaction_ref")}),
        ("Finances", {"fields": ("total_interest", "total_due", "total_repaid", "balance_remaining", "repayment_progress_pct")}),
    )


@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display  = ("loan", "amount_paid", "principal_part", "interest_part", "balance_after", "payment_method", "paid_at")
    list_filter   = ("payment_method",)
    search_fields = ("loan__membership__user__username", "transaction_ref")
    readonly_fields = ("paid_at", "principal_part", "interest_part", "balance_after")


# ── Notifications & Documents ─────────────────────────────────────────────────

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ("membership", "type", "title", "is_read", "created_at")
    list_filter   = ("type", "is_read")
    search_fields = ("membership__user__username", "title")
    readonly_fields = ("created_at", "read_at")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display  = ("group", "type", "title", "uploaded_by", "created_at")
    list_filter   = ("type", "group")
    search_fields = ("title", "group__name")
