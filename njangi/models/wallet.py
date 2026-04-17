"""
Njangi+ — Wallet & Relevés mensuels d'intérêts

Logique :
  Chaque mois, les dépôts actifs des membres constituent un "pool".
  Ce pool finance les prêts actifs.
  Les intérêts générés par les prêts sont redistribués
  proportionnellement à la part de chaque déposant dans le pool.

  Formule :
    pool_total = Σ dépôts actifs ce mois
    interest_total = Σ (loan.amount_approved × loan.interest_rate/100) par prêt actif
    interest_member = (deposit_member / pool_total) × interest_total
"""
from django.db import models


class MonthlyGroupInterest(models.Model):
    """Enregistrement mensuel des intérêts générés au niveau du groupe."""

    group  = models.ForeignKey(
        "njangi.Group", on_delete=models.CASCADE,
        related_name="monthly_interests",
        verbose_name="Groupe"
    )
    year   = models.PositiveSmallIntegerField(verbose_name="Année")
    month  = models.PositiveSmallIntegerField(verbose_name="Mois (1-12)")

    # Snapshot des montants clés ce mois
    total_pool                = models.DecimalField(max_digits=16, decimal_places=0, default=0, verbose_name="Pool total (FCFA)")
    total_loans_outstanding   = models.DecimalField(max_digits=16, decimal_places=0, default=0, verbose_name="Encours prêts (FCFA)")
    total_interest_generated  = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="Intérêts générés (FCFA)")
    nb_active_loans           = models.PositiveSmallIntegerField(default=0, verbose_name="Nombre de prêts actifs")
    nb_depositors             = models.PositiveSmallIntegerField(default=0, verbose_name="Nombre de déposants")

    is_calculated  = models.BooleanField(default=False, verbose_name="Calculé")
    calculated_at  = models.DateTimeField(null=True, blank=True, verbose_name="Calculé le")

    class Meta:
        verbose_name = "Intérêts mensuels groupe"
        verbose_name_plural = "Intérêts mensuels groupes"
        unique_together = ("group", "year", "month")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.group.name} — {self.month:02d}/{self.year} | {self.formatted_interest}"

    @property
    def period_label(self):
        months_fr = ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
                     "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        return f"{months_fr[self.month]} {self.year}"

    @property
    def formatted_interest(self):
        return f"{int(self.total_interest_generated):,}".replace(",", " ") + " FCFA"

    @property
    def formatted_pool(self):
        return f"{int(self.total_pool):,}".replace(",", " ") + " FCFA"

    @property
    def utilization_rate(self):
        """% du pool effectivement prêté."""
        if not self.total_pool:
            return 0
        return min(100, int(self.total_loans_outstanding / self.total_pool * 100))


class MemberMonthlyStatement(models.Model):
    """Relevé mensuel d'un membre — ses avoirs et ses intérêts gagnés."""

    membership     = models.ForeignKey(
        "njangi.Membership", on_delete=models.CASCADE,
        related_name="monthly_statements",
        verbose_name="Membre"
    )
    monthly_record = models.ForeignKey(
        MonthlyGroupInterest, on_delete=models.CASCADE,
        related_name="member_statements",
        verbose_name="Mois"
    )

    # Situation du membre ce mois
    deposit_balance      = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="Dépôt actif (FCFA)")
    pool_share_pct       = models.DecimalField(max_digits=6,  decimal_places=2, default=0, verbose_name="Part dans le pool (%)")
    contribution_to_loans = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="Contribution aux prêts (FCFA)")

    # Intérêts
    interest_earned      = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Intérêts gagnés ce mois (FCFA)")
    cumulative_interest  = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="Intérêts cumulés (FCFA)")

    # Avoirs totaux
    wallet_balance       = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="Avoirs totaux (FCFA)")

    class Meta:
        verbose_name = "Relevé mensuel membre"
        verbose_name_plural = "Relevés mensuels membres"
        unique_together = ("membership", "monthly_record")
        ordering = ["-monthly_record__year", "-monthly_record__month"]

    def __str__(self):
        return (
            f"{self.membership.user} — {self.monthly_record.period_label} "
            f"| +{self.formatted_interest}"
        )

    @property
    def year(self):
        return self.monthly_record.year

    @property
    def month(self):
        return self.monthly_record.month

    @property
    def period_label(self):
        return self.monthly_record.period_label

    @property
    def formatted_interest(self):
        return f"{int(self.interest_earned):,}".replace(",", " ") + " FCFA"

    @property
    def formatted_wallet(self):
        return f"{int(self.wallet_balance):,}".replace(",", " ") + " FCFA"

    @property
    def formatted_deposit(self):
        return f"{int(self.deposit_balance):,}".replace(",", " ") + " FCFA"

    @property
    def formatted_cumulative(self):
        return f"{int(self.cumulative_interest):,}".replace(",", " ") + " FCFA"
