from django.db import transaction as db_transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from tchaslucpay.transactions.models import Transaction, TransactionStatus

from .tasks import send_email_notification, send_sms_notification


def _enqueue_notifications(transaction):
    try:
        send_sms_notification.delay(transaction.pk)
    except Exception:
        # Repli local: le message est tout de meme genere et journalise.
        send_sms_notification.run(transaction.pk)

    try:
        send_email_notification.delay(transaction.pk)
    except Exception:
        # Repli local: le message est tout de meme genere et journalise.
        send_email_notification.run(transaction.pk)


@receiver(post_save, sender=Transaction)
def notify_transaction_validated(sender, instance, created, **kwargs):
    """Declenche les notifications sans bloquer l'enregistrement comptable."""
    if not created:
        return

    statuts_valides = {TransactionStatus.POSTED, "VALIDEE"}
    if instance.status not in statuts_valides:
        return

    db_transaction.on_commit(lambda tx=instance: _enqueue_notifications(tx))
