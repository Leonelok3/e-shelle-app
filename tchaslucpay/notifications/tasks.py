from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

try:
    from celery import shared_task
except ImportError:
    def shared_task(*dargs, **dkwargs):
        def decorator(func):
            return func
        return decorator

from tchaslucpay.transactions.models import Transaction, TransactionType

from .models import NotificationChannel, NotificationLog, NotificationStatus


def _collecteur_label(transaction):
    collecteur = transaction.collector
    if collecteur is None:
        return "votre collecteur"
    return collecteur.get_full_name() or collecteur.username


def _format_xaf(value):
    """Formate un montant XAF sans decimales, avec espaces de milliers."""
    return f"{value:,.0f}".replace(",", " ")


def _message_transaction(transaction):
    """Construit le message client exactement selon le cahier des charges."""
    created_at = timezone.localtime(transaction.created_at)
    date = created_at.strftime("%d/%m/%Y")
    heure = created_at.strftime("%H:%M")
    montant = _format_xaf(transaction.amount)
    ancien_solde = _format_xaf(transaction.balance_before)
    nouveau_solde = _format_xaf(transaction.balance_after)
    collecteur = _collecteur_label(transaction)

    if transaction.transaction_type == TransactionType.WITHDRAWAL:
        return (
            f"Vous avez effectué un retrait de {montant} XAF auprès de {collecteur}, "
            f"le {date} à {heure}. TRID: {transaction.trid}. "
            f"Solde restant : {nouveau_solde} XAF."
        )

    return (
        f"Vous avez effectué une collecte Tchaslucpay de {montant} XAF auprès de {collecteur}, "
        f"le {date} à {heure}. TRID: {transaction.trid}. "
        f"Solde : {ancien_solde} XAF. Votre nouveau solde est de {nouveau_solde} XAF."
    )


def _create_log(transaction, channel, recipient, subject=""):
    return NotificationLog.objects.create(
        user=transaction.account,
        channel=channel,
        recipient=recipient,
        subject=subject,
        message=_message_transaction(transaction),
        status=NotificationStatus.QUEUED,
        metadata={"transaction_id": transaction.pk, "trid": transaction.trid},
    )


def _mark_failure(log, exc):
    log.status = NotificationStatus.ECHEC
    log.error_message = str(exc)
    log.save(update_fields=["status", "error_message"])


@shared_task(bind=True, max_retries=0)
def send_sms_notification(self, transaction_id):
    transaction = Transaction.objects.select_related("account", "collector").get(pk=transaction_id)
    recipient = getattr(transaction.account, "phone_number", "") or ""
    if not recipient:
        return None

    log = _create_log(transaction, NotificationChannel.SMS, recipient)
    try:
        if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_FROM_NUMBER]):
            # En local, l'absence de Twilio simule un envoi reussi sans bloquer le flux.
            log.provider_reference = "SIMULATED_SMS"
        else:
            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            sent = client.messages.create(body=log.message, from_=settings.TWILIO_FROM_NUMBER, to=recipient)
            log.provider_reference = sent.sid
        log.status = NotificationStatus.ENVOYEE
        log.sent_at = timezone.now()
        log.save(update_fields=["status", "provider_reference", "sent_at"])
    except Exception as exc:
        _mark_failure(log, exc)
    return log.pk


@shared_task(bind=True, max_retries=0)
def send_email_notification(self, transaction_id):
    transaction = Transaction.objects.select_related("account", "collector").get(pk=transaction_id)
    recipient = getattr(transaction.account, "email", "") or ""
    if not recipient:
        return None

    log = _create_log(transaction, NotificationChannel.EMAIL, recipient, subject="Votre transaction Tchaslucpay")
    try:
        sent_count = send_mail(log.subject, log.message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
        if not sent_count:
            raise RuntimeError("Aucun email envoye par le backend.")
        log.status = NotificationStatus.ENVOYEE
        log.sent_at = timezone.now()
        log.save(update_fields=["status", "sent_at"])
    except Exception as exc:
        _mark_failure(log, exc)
    return log.pk


# Compatibilite avec les anciens appels internes deja presents dans le module.
send_sms = send_sms_notification
send_email = send_email_notification
