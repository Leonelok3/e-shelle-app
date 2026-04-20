"""
Njangi+ — Signaux Django

Responsabilités :
  1. Notifications in-app aux membres (contribution payée, prêt approuvé…)
  2. Audit trail automatique (qui a fait quoi et quand)
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


# ── Helpers audit ─────────────────────────────────────────────────────────────

def _audit(group, action, description, user=None, model_name="", object_id=None, extra=None):
    """Crée une entrée d'audit de façon sécurisée (ignore les erreurs)."""
    try:
        from njangi.models.audit import AuditLog
        AuditLog.log(
            group=group, action=action, description=description,
            user=user, model_name=model_name, object_id=object_id, extra=extra or {},
        )
    except Exception:
        pass  # Ne jamais planter l'opération principale à cause de l'audit


# ── Signal 1 — Cotisations ────────────────────────────────────────────────────

@receiver(post_save, sender="njangi.Contribution")
def notify_contribution_paid(sender, instance, created, **kwargs):
    """Notifie le membre et enregistre dans l'audit quand une cotisation est payée."""
    if not created and instance.status == "paid":
        from njangi.models.notification import Notification

        Notification.send(
            membership=instance.membership,
            notif_type="contribution_due",
            title="Cotisation enregistrée",
            body=f"Votre cotisation de {int(instance.amount_paid):,} FCFA pour la séance #{instance.session.session_number} a été enregistrée.",
            reference_session=instance.session,
        )
        _audit(
            group=instance.membership.group,
            action="contribution_paid",
            description=f"{instance.membership.user} — cotisation séance #{instance.session.session_number} : {int(instance.amount_paid):,} FCFA",
            user=instance.recorded_by,
            model_name="Contribution",
            object_id=instance.pk,
            extra={"amount": int(instance.amount_paid), "method": instance.payment_method},
        )

    elif not created and instance.status == "late" and instance.penalty_amount > 0:
        _audit(
            group=instance.membership.group,
            action="contribution_penalized",
            description=f"{instance.membership.user} — pénalité {int(instance.penalty_amount):,} FCFA ({instance.days_late} jours de retard)",
            model_name="Contribution",
            object_id=instance.pk,
            extra={"penalty": int(instance.penalty_amount), "days_late": instance.days_late},
        )


# ── Signal 2 — Prêts ──────────────────────────────────────────────────────────

@receiver(post_save, sender="njangi.Loan")
def notify_loan_status_change(sender, instance, created, **kwargs):
    """Notifie le membre et audite les changements de statut du prêt."""
    from njangi.models.notification import Notification

    if created:
        _audit(
            group=instance.membership.group,
            action="loan_requested",
            description=f"{instance.membership.user} demande un prêt de {int(instance.amount_requested):,} FCFA ({instance.duration_months} mois)",
            model_name="Loan",
            object_id=instance.pk,
            extra={"amount": int(instance.amount_requested), "months": instance.duration_months},
        )
        return

    if instance.status == "approved":
        Notification.send(
            membership=instance.membership,
            notif_type="loan_approved",
            title="Prêt approuvé",
            body=f"Votre demande de prêt de {int(instance.amount_approved):,} FCFA a été approuvée.",
            reference_loan=instance,
        )
        _audit(
            group=instance.membership.group,
            action="loan_approved",
            description=f"Prêt approuvé pour {instance.membership.user} : {int(instance.amount_approved):,} FCFA",
            user=instance.reviewed_by,
            model_name="Loan",
            object_id=instance.pk,
            extra={"amount": int(instance.amount_approved), "rate": float(instance.interest_rate)},
        )
    elif instance.status == "rejected":
        Notification.send(
            membership=instance.membership,
            notif_type="loan_rejected",
            title="Demande de prêt refusée",
            body=f"Votre demande de prêt a été refusée. Motif : {instance.rejection_reason or 'Non précisé'}.",
            reference_loan=instance,
        )
        _audit(
            group=instance.membership.group,
            action="loan_rejected",
            description=f"Prêt refusé pour {instance.membership.user} — {instance.rejection_reason or 'Sans motif'}",
            user=instance.reviewed_by,
            model_name="Loan",
            object_id=instance.pk,
        )
    elif instance.status == "active":
        Notification.send(
            membership=instance.membership,
            notif_type="loan_disbursed",
            title="Prêt décaissé",
            body=f"{int(instance.amount_approved):,} FCFA ont été versés sur votre compte. Échéance : {instance.due_date}.",
            reference_loan=instance,
        )
        _audit(
            group=instance.membership.group,
            action="loan_disbursed",
            description=f"Prêt décaissé — {instance.membership.user} : {int(instance.amount_approved):,} FCFA | Échéance: {instance.due_date}",
            model_name="Loan",
            object_id=instance.pk,
            extra={"amount": int(instance.amount_approved), "due_date": str(instance.due_date)},
        )
    elif instance.status == "completed":
        _audit(
            group=instance.membership.group,
            action="loan_completed",
            description=f"Prêt entièrement remboursé — {instance.membership.user} : {int(instance.amount_approved):,} FCFA",
            model_name="Loan",
            object_id=instance.pk,
        )
    elif instance.status == "defaulted":
        _audit(
            group=instance.membership.group,
            action="loan_defaulted",
            description=f"Prêt en DÉFAUT — {instance.membership.user} : {int(instance.balance_remaining):,} FCFA restants | Échu le {instance.due_date}",
            model_name="Loan",
            object_id=instance.pk,
            extra={"balance_remaining": int(instance.balance_remaining)},
        )


# ── Signal 3 — Dépôts ────────────────────────────────────────────────────────

@receiver(post_save, sender="njangi.FundDeposit")
def notify_deposit_withdrawn(sender, instance, created, **kwargs):
    """Notifie et audite les dépôts/retraits du fond commun."""
    from njangi.models.notification import Notification

    if created:
        _audit(
            group=instance.membership.group,
            action="deposit_created",
            description=f"{instance.membership.user} — nouveau dépôt : {int(instance.amount):,} FCFA ({instance.duration_months} mois à {instance.interest_rate}%)",
            model_name="FundDeposit",
            object_id=instance.pk,
            extra={"amount": int(instance.amount), "months": instance.duration_months, "rate": float(instance.interest_rate)},
        )
        return

    if instance.status == "withdrawn":
        Notification.send(
            membership=instance.membership,
            notif_type="deposit_matured",
            title="Dépôt retiré",
            body=(
                f"Votre dépôt de {int(instance.amount):,} FCFA + "
                f"{int(instance.interest_earned):,} FCFA d'intérêts ont été retirés. "
                f"Total : {int(instance.withdrawn_amount):,} FCFA."
            ),
            reference_deposit=instance,
        )
        _audit(
            group=instance.membership.group,
            action="deposit_withdrawn",
            description=f"{instance.membership.user} — retrait dépôt : {int(instance.amount):,} FCFA + {int(instance.interest_earned):,} FCFA intérêts = {int(instance.withdrawn_amount):,} FCFA",
            model_name="FundDeposit",
            object_id=instance.pk,
            extra={"principal": int(instance.amount), "interest": int(instance.interest_earned), "total": int(instance.withdrawn_amount)},
        )


# ── Signal 4 — Membership (rejoindre/quitter) ─────────────────────────────────

@receiver(post_save, sender="njangi.Membership")
def audit_membership_change(sender, instance, created, **kwargs):
    """Audite les changements de membership."""
    if created:
        _audit(
            group=instance.group,
            action="member_joined",
            description=f"{instance.user} a rejoint le groupe en tant que {instance.get_role_display()}",
            model_name="Membership",
            object_id=instance.pk,
            extra={"role": instance.role},
        )


# ── Signal 5 — Remboursements ─────────────────────────────────────────────────

@receiver(post_save, sender="njangi.LoanRepayment")
def audit_loan_repayment(sender, instance, created, **kwargs):
    """Audite les remboursements de prêt."""
    if created:
        _audit(
            group=instance.loan.membership.group,
            action="loan_repayment",
            description=(
                f"{instance.loan.membership.user} — remboursement {int(instance.amount_paid):,} FCFA "
                f"(capital: {int(instance.principal_part):,} | intérêts: {int(instance.interest_part):,}) "
                f"| Reste: {int(instance.balance_after):,} FCFA"
            ),
            user=instance.recorded_by,
            model_name="LoanRepayment",
            object_id=instance.pk,
            extra={
                "amount": int(instance.amount_paid),
                "principal": int(instance.principal_part),
                "interest": int(instance.interest_part),
                "balance_after": int(instance.balance_after),
            },
        )
