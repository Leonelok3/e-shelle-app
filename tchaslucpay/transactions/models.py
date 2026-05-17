from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class TransactionType(models.TextChoices):
    DEPOSIT = "DEPOSIT", "Depot"
    WITHDRAWAL = "WITHDRAWAL", "Retrait"
    CONTRIBUTION = "CONTRIBUTION", "Cotisation tontine"
    LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT", "Decaissement pret"
    LOAN_REPAYMENT = "LOAN_REPAYMENT", "Remboursement pret"
    FEE = "FEE", "Frais"
    REVERSAL = "REVERSAL", "Annulation comptable"


class TransactionStatus(models.TextChoices):
    PENDING = "PENDING", "En attente"
    POSTED = "POSTED", "Validee"
    REVERSED = "REVERSED", "Annulee"
    FAILED = "FAILED", "Echouee"


class AccountBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tchaslucpay_balance")
    available_balance = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    locked_balance = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=3, default="XAF")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solde client"
        verbose_name_plural = "Soldes clients"

    @property
    def total_balance(self):
        return self.available_balance + self.locked_balance


class Transaction(models.Model):
    trid = models.CharField(max_length=40, unique=True, db_index=True)
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tchaslucpay_transactions")
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tchaslucpay_collected_transactions",
    )
    transaction_type = models.CharField(max_length=30, choices=TransactionType.choices, db_index=True)
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.POSTED, db_index=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(Decimal("1.00"))])
    balance_before = models.DecimalField(max_digits=18, decimal_places=2)
    balance_after = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, default="XAF")
    external_reference = models.CharField(max_length=100, blank=True, db_index=True)
    description = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    reversed_transaction = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="reversal_entries")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tchaslucpay_created_transactions")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["account", "created_at"]),
            models.Index(fields=["transaction_type", "status"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name="tchaslucpay_transaction_amount_positive"),
        ]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.trid} - {self.transaction_type} - {self.amount} {self.currency}"

    @property
    def amount_display(self):
        return f"{self.amount:,.0f} {self.currency}".replace(",", " ")

