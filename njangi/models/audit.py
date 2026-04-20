"""
Njangi+ — Audit Trail

Enregistre toutes les actions importantes sur le groupe :
qui a fait quoi, quand, et sur quel objet.
"""
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Journal d'audit des actions sur un groupe Njangi."""

    ACTION_CHOICES = [
        # Sessions
        ("session_created",        "Séance créée"),
        ("session_opened",         "Séance ouverte"),
        ("session_closed",         "Séance clôturée"),
        # Cotisations
        ("contribution_paid",      "Cotisation payée"),
        ("contribution_penalized", "Cotisation pénalisée"),
        # Prêts
        ("loan_requested",         "Prêt demandé"),
        ("loan_approved",          "Prêt approuvé"),
        ("loan_rejected",          "Prêt refusé"),
        ("loan_disbursed",         "Prêt décaissé"),
        ("loan_repayment",         "Remboursement enregistré"),
        ("loan_completed",         "Prêt remboursé intégralement"),
        ("loan_defaulted",         "Prêt en défaut"),
        # Dépôts
        ("deposit_created",        "Dépôt créé"),
        ("deposit_withdrawn",      "Dépôt retiré"),
        # Membres
        ("member_joined",          "Membre rejoint"),
        ("member_left",            "Membre parti"),
        ("role_changed",           "Rôle modifié"),
        # Abonnements
        ("plan_upgraded",          "Plan mis à niveau"),
        ("plan_rejected",          "Demande plan refusée"),
        # Fond
        ("fund_adjustment",        "Ajustement fond commun"),
        ("interest_calculated",    "Intérêts calculés"),
        # Divers
        ("other",                  "Autre"),
    ]

    group       = models.ForeignKey(
        "njangi.Group", on_delete=models.CASCADE,
        related_name="audit_logs",
        verbose_name="Groupe"
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="njangi_audit_logs",
        verbose_name="Réalisé par"
    )

    action      = models.CharField(max_length=30, choices=ACTION_CHOICES, verbose_name="Action")
    model_name  = models.CharField(max_length=50, blank=True, verbose_name="Modèle concerné")
    object_id   = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID objet")
    description = models.TextField(verbose_name="Description")

    # Données extra optionnelles (montants, anciens/nouveaux statuts, etc.)
    extra       = models.JSONField(default=dict, blank=True, verbose_name="Données extra")

    created_at  = models.DateTimeField(auto_now_add=True, verbose_name="Date/heure")

    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journal d'audit"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["group", "-created_at"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        who = self.performed_by.username if self.performed_by else "système"
        return f"[{self.created_at:%d/%m/%Y %H:%M}] {self.get_action_display()} — {who}"

    @classmethod
    def log(cls, group, action, description, user=None, model_name="", object_id=None, extra=None):
        """Raccourci pour créer une entrée d'audit."""
        return cls.objects.create(
            group=group,
            performed_by=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            description=description,
            extra=extra or {},
        )
