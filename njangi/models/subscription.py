"""
Njangi+ — Demandes d'abonnement
Le fondateur reçoit le paiement (MoMo/dépôt) et active manuellement depuis l'admin.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class SubscriptionRequest(models.Model):
    """Demande d'activation/renouvellement de plan envoyée par un président de groupe."""

    PLAN_CHOICES = [
        ("standard",    "Standard — 3 000 FCFA/mois"),
        ("pro",         "Pro — 7 000 FCFA/mois"),
        ("association", "Association — 15 000 FCFA/mois"),
    ]
    PAYMENT_CHOICES = [
        ("mtn_momo",    "MTN Mobile Money"),
        ("orange_money","Orange Money"),
        ("depot_banque","Dépôt bancaire"),
        ("autre",       "Autre"),
    ]
    STATUS_CHOICES = [
        ("pending",  "En attente"),
        ("approved", "Approuvé"),
        ("rejected", "Refusé"),
    ]
    DURATION_CHOICES = [
        (1,  "1 mois"),
        (3,  "3 mois  (-5%)"),
        (6,  "6 mois  (-10%)"),
        (12, "12 mois (-15%)"),
    ]

    group            = models.ForeignKey("njangi.Group", on_delete=models.CASCADE, related_name="subscription_requests")
    requested_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="njangi_sub_requests")

    plan             = models.CharField(max_length=15, choices=PLAN_CHOICES)
    duration_months  = models.PositiveSmallIntegerField(default=1, choices=DURATION_CHOICES, verbose_name="Durée")
    amount_expected  = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Montant attendu (FCFA)")
    amount_paid      = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Montant déclaré (FCFA)")

    payment_method   = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name="Méthode de paiement")
    phone_used       = models.CharField(max_length=20, blank=True, verbose_name="Numéro utilisé")
    payment_date     = models.DateField(verbose_name="Date du paiement")
    payment_ref      = models.CharField(max_length=100, blank=True, verbose_name="Référence / reçu")
    notes            = models.TextField(blank=True, verbose_name="Notes")

    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    processed_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="njangi_sub_processed"
    )
    processed_at     = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Demande d'abonnement"
        verbose_name_plural = "Demandes d'abonnement"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.group.name} — {self.get_plan_display()} × {self.duration_months} mois ({self.get_status_display()})"

    def compute_amount(self):
        """Calcule le montant attendu selon le plan et la durée (avec remises)."""
        from njangi.models.group import PLAN_CONFIG
        base = PLAN_CONFIG.get(self.plan, {}).get("price", 0)
        discount = {1: 0, 3: 0.05, 6: 0.10, 12: 0.15}.get(self.duration_months, 0)
        self.amount_expected = int(base * self.duration_months * (1 - discount))

    def approve(self, admin_user):
        """Active le plan sur le groupe."""
        group = self.group
        now = timezone.now()

        # Si déjà actif et pas expiré → prolonger
        if group.plan == self.plan and group.plan_expires_at and group.plan_expires_at > now:
            group.plan_expires_at += relativedelta(months=self.duration_months)
        else:
            group.plan_expires_at = now + relativedelta(months=self.duration_months)

        group.plan = self.plan
        group.plan_note = f"Activé par {admin_user} le {now.strftime('%d/%m/%Y')}"
        group.save(update_fields=["plan", "plan_expires_at", "plan_note"])

        self.status = "approved"
        self.processed_by = admin_user
        self.processed_at = now
        self.save(update_fields=["status", "processed_by", "processed_at"])

    def reject(self, admin_user, reason=""):
        self.status = "rejected"
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=["status", "processed_by", "processed_at", "rejection_reason"])
