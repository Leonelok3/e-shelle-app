"""
Njangi+ — Notifications & Documents
"""
from django.db import models


class Notification(models.Model):
    """Notification in-app pour un membre."""

    TYPE_CHOICES = [
        ("session_planned",    "Séance planifiée"),
        ("session_reminder",   "Rappel séance"),
        ("contribution_due",   "Cotisation due"),
        ("contribution_late",  "Cotisation en retard"),
        ("hand_received",      "Main reçue"),
        ("loan_approved",      "Prêt approuvé"),
        ("loan_rejected",      "Prêt refusé"),
        ("loan_disbursed",     "Prêt décaissé"),
        ("repayment_due",      "Remboursement dû"),
        ("repayment_recorded", "Remboursement enregistré"),
        ("deposit_matured",    "Dépôt arrivé à échéance"),
        ("member_joined",      "Nouveau membre"),
        ("general",            "Général"),
    ]

    membership  = models.ForeignKey(
        "njangi.Membership", on_delete=models.CASCADE,
        related_name="notifications", verbose_name="Membre"
    )
    type        = models.CharField(max_length=25, choices=TYPE_CHOICES, default="general")
    title       = models.CharField(max_length=120)
    body        = models.TextField()
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    read_at     = models.DateTimeField(null=True, blank=True)

    # Liens optionnels vers les objets concernés
    reference_session  = models.ForeignKey("njangi.Session",  on_delete=models.SET_NULL, null=True, blank=True)
    reference_loan     = models.ForeignKey("njangi.Loan",     on_delete=models.SET_NULL, null=True, blank=True)
    reference_deposit  = models.ForeignKey("njangi.FundDeposit", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.membership.user} — {self.title}"

    def mark_read(self):
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

    @classmethod
    def send(cls, membership, notif_type, title, body, **kwargs):
        """Crée une notification et déclenche envoi SMS/WhatsApp si activé."""
        return cls.objects.create(
            membership=membership,
            type=notif_type,
            title=title,
            body=body,
            **{k: v for k, v in kwargs.items() if k in (
                "reference_session", "reference_loan", "reference_deposit"
            )},
        )


class Document(models.Model):
    """Document partagé dans un groupe (règlement, PV, relevé...)."""

    TYPE_CHOICES = [
        ("rules",    "Règlement intérieur"),
        ("pv",       "Procès-verbal de séance"),
        ("statement","Relevé de compte"),
        ("contract", "Contrat de prêt"),
        ("other",    "Autre"),
    ]

    group       = models.ForeignKey("njangi.Group", on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.SET_NULL, null=True,
        related_name="njangi_documents_uploaded"
    )
    type        = models.CharField(max_length=15, choices=TYPE_CHOICES, default="other")
    title       = models.CharField(max_length=200)
    file        = models.FileField(upload_to="njangi/documents/")
    created_at  = models.DateTimeField(auto_now_add=True)

    # Lien optionnel vers une séance
    reference_session = models.ForeignKey(
        "njangi.Session", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="documents"
    )

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.group.name} — {self.title}"
