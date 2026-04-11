"""
Njangi+ — Fond commun : Dépôts & Transactions
"""
from django.db import models
from django.utils import timezone


class FundDeposit(models.Model):
    """Dépôt volontaire d'un membre dans le fond commun pour générer des intérêts."""

    STATUS_CHOICES = [
        ("active",    "Actif"),
        ("withdrawn", "Retiré"),
        ("expired",   "Échu"),
    ]

    membership     = models.ForeignKey("njangi.Membership", on_delete=models.CASCADE, related_name="fund_deposits")
    amount         = models.DecimalField(max_digits=14, decimal_places=0, verbose_name="Montant déposé (FCFA)")
    deposited_at   = models.DateTimeField(auto_now_add=True)
    duration_months = models.PositiveSmallIntegerField(default=3, verbose_name="Durée (mois)")
    interest_rate  = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taux d'intérêt (%/mois)")

    # Résultats
    interest_earned = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Intérêts gagnés (FCFA)")
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    withdrawn_at    = models.DateTimeField(null=True, blank=True)
    withdrawn_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)

    payment_method  = models.CharField(max_length=20, blank=True)
    transaction_ref = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Dépôt fond commun"
        verbose_name_plural = "Dépôts fond commun"
        ordering = ["-deposited_at"]

    def __str__(self):
        return f"{self.membership.user} — {self.formatted_amount} ({self.get_status_display()})"

    @property
    def expected_interest(self):
        """Intérêts attendus à terme."""
        return int(self.amount * self.interest_rate / 100 * self.duration_months)

    @property
    def months_elapsed(self):
        from dateutil.relativedelta import relativedelta
        end = self.withdrawn_at or timezone.now()
        delta = relativedelta(end, self.deposited_at)
        return min(delta.months + delta.years * 12, self.duration_months)

    @property
    def current_interest(self):
        """Intérêts accumulés à ce jour."""
        return int(self.amount * self.interest_rate / 100 * self.months_elapsed)

    @property
    def maturity_date(self):
        from dateutil.relativedelta import relativedelta
        return self.deposited_at + relativedelta(months=self.duration_months)

    @property
    def formatted_amount(self):
        return f"{int(self.amount):,}".replace(",", " ") + " FCFA"

    def withdraw(self, user=None):
        """Retirer le dépôt + intérêts accumulés."""
        self.interest_earned = self.current_interest
        self.withdrawn_amount = self.amount + self.interest_earned
        self.withdrawn_at = timezone.now()
        self.status = "withdrawn"
        self.save()

        # Enregistrer la sortie dans le fond
        FundTransaction.objects.create(
            group=self.membership.group,
            type="deposit_out",
            amount=self.withdrawn_amount,
            description=f"Retrait dépôt + intérêts — {self.membership.user}",
            reference_deposit=self,
        )


class FundTransaction(models.Model):
    """Mouvement financier du fond commun — audit trail complet."""

    TYPE_CHOICES = [
        ("deposit_in",   "Dépôt entrant"),
        ("deposit_out",  "Retrait dépôt"),
        ("loan_out",     "Prêt accordé"),
        ("repayment",    "Remboursement prêt"),
        ("interest_in",  "Intérêts prêt reçus"),
        ("interest_out", "Intérêts dépôt versés"),
        ("penalty_in",   "Pénalités encaissées"),
        ("hand_paid",    "Main versée au bénéficiaire"),
        ("expense",      "Dépense du groupe"),
        ("adjustment",   "Ajustement manuel"),
    ]

    group       = models.ForeignKey("njangi.Group", on_delete=models.CASCADE, related_name="fund_transactions")
    type        = models.CharField(max_length=15, choices=TYPE_CHOICES)
    amount      = models.DecimalField(max_digits=14, decimal_places=0, verbose_name="Montant (FCFA)")
    # Positif = entrée fond, Négatif = sortie fond
    signed_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    balance_after = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="Solde après (FCFA)")

    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    created_by  = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="njangi_fund_transactions"
    )

    # Références optionnelles
    reference_loan    = models.ForeignKey("njangi.Loan", on_delete=models.SET_NULL, null=True, blank=True)
    reference_deposit = models.ForeignKey(FundDeposit, on_delete=models.SET_NULL, null=True, blank=True)
    reference_session = models.ForeignKey("njangi.Session", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Transaction fond commun"
        verbose_name_plural = "Transactions fond commun"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.group.name} — {self.get_type_display()} {self.formatted_amount}"

    def save(self, *args, **kwargs):
        # Définir le signe automatiquement
        outgoing = {"deposit_out", "loan_out", "interest_out", "hand_paid", "expense"}
        self.signed_amount = -self.amount if self.type in outgoing else self.amount
        super().save(*args, **kwargs)

    @property
    def formatted_amount(self):
        return f"{int(self.amount):,}".replace(",", " ") + " FCFA"

    @property
    def is_credit(self):
        return self.signed_amount > 0
