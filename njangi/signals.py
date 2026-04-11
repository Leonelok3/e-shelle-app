"""
Njangi+ — Signaux Django
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="njangi.Contribution")
def notify_contribution_paid(sender, instance, created, **kwargs):
    """Notifie le trésorier quand une cotisation est marquée payée."""
    if not created and instance.status == "paid":
        from njangi.models.notification import Notification
        from njangi.models.group import Membership

        # Notification au membre
        Notification.send(
            membership=instance.membership,
            notif_type="contribution_due",
            title="Cotisation enregistrée",
            body=f"Votre cotisation de {instance.amount_paid:,} FCFA pour la séance #{instance.session.session_number} a été enregistrée.",
            reference_session=instance.session,
        )


@receiver(post_save, sender="njangi.Loan")
def notify_loan_status_change(sender, instance, created, **kwargs):
    """Notifie le membre des changements de statut de son prêt."""
    from njangi.models.notification import Notification

    if created:
        return  # Pas de notif à la création (en attente)

    if instance.status == "approved":
        Notification.send(
            membership=instance.membership,
            notif_type="loan_approved",
            title="Prêt approuvé",
            body=f"Votre demande de prêt de {int(instance.amount_approved):,} FCFA a été approuvée.",
            reference_loan=instance,
        )
    elif instance.status == "rejected":
        Notification.send(
            membership=instance.membership,
            notif_type="loan_rejected",
            title="Demande de prêt refusée",
            body=f"Votre demande de prêt a été refusée. Motif : {instance.rejection_reason or 'Non précisé'}.",
            reference_loan=instance,
        )
    elif instance.status == "active":
        Notification.send(
            membership=instance.membership,
            notif_type="loan_disbursed",
            title="Prêt décaissé",
            body=f"{int(instance.amount_approved):,} FCFA ont été versés sur votre compte. Échéance : {instance.due_date}.",
            reference_loan=instance,
        )


@receiver(post_save, sender="njangi.FundDeposit")
def notify_deposit_withdrawn(sender, instance, created, **kwargs):
    """Notifie le membre quand son dépôt est retiré."""
    from njangi.models.notification import Notification

    if not created and instance.status == "withdrawn":
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
