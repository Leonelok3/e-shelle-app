"""
signals.py — auto_cameroun
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail

from .models import Vehicule, ProfilAuto, StatutVehicule, DemandeEssai


@receiver(post_save, sender=Vehicule)
def notifier_statut_vehicule(sender, instance, created, **kwargs):
    """Email au propriétaire quand un véhicule est publié ou refusé."""
    if not created:
        if instance.statut == StatutVehicule.PUBLIE:
            try:
                send_mail(
                    subject=f"✅ Votre annonce est publiée — {instance.marque} {instance.modele}",
                    message=(
                        f"Bonjour {instance.proprietaire.get_full_name() or instance.proprietaire.username},\n\n"
                        f"Votre annonce « {instance.marque} {instance.modele} {instance.annee} » est maintenant en ligne.\n\n"
                        f"Bonne vente !\nL'équipe Auto Cameroun"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.proprietaire.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        elif instance.statut == StatutVehicule.REFUSE:
            try:
                note = instance.note_admin or "Aucune note fournie."
                send_mail(
                    subject=f"❌ Annonce refusée — {instance.marque} {instance.modele}",
                    message=(
                        f"Bonjour {instance.proprietaire.get_full_name() or instance.proprietaire.username},\n\n"
                        f"Votre annonce « {instance.marque} {instance.modele} {instance.annee} » a été refusée.\n"
                        f"Motif : {note}\n\nContactez-nous pour plus d'informations.\nL'équipe Auto Cameroun"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.proprietaire.email],
                    fail_silently=True,
                )
            except Exception:
                pass


@receiver(post_save, sender=DemandeEssai)
def notifier_demande_essai(sender, instance, created, **kwargs):
    """Email au propriétaire quand une demande d'essai est reçue."""
    if created:
        try:
            send_mail(
                subject=f"🔑 Nouvelle demande d'essai — {instance.vehicule.marque} {instance.vehicule.modele}",
                message=(
                    f"Bonjour,\n\nVous avez une nouvelle demande d'essai :\n"
                    f"- Véhicule : {instance.vehicule.marque} {instance.vehicule.modele} {instance.vehicule.annee}\n"
                    f"- Client : {instance.nom_complet}\n"
                    f"- Téléphone : {instance.telephone}\n"
                    f"- Email : {instance.email or 'Non renseigné'}\n"
                    f"- Date souhaitée : {instance.date_souhaitee}\n"
                    f"- Message : {instance.message or 'Aucun'}\n\n"
                    f"Connectez-vous à votre espace pour gérer cette demande.\nL'équipe Auto Cameroun"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.vehicule.proprietaire.email],
                fail_silently=True,
            )
        except Exception:
            pass


_profil_ancien_compte = {}

@receiver(post_save, sender=ProfilAuto, dispatch_uid="auto_profil_save")
def mettre_en_avant_vehicules_premium(sender, instance, created, **kwargs):
    """Met automatiquement en avant tous les véhicules quand le compte passe en Premium."""
    if not created and instance.est_premium:
        ancien = _profil_ancien_compte.get(instance.pk)
        if ancien and ancien != "PREMIUM":
            instance.user.vehicules.filter(statut=StatutVehicule.PUBLIE).update(est_mis_en_avant=True)
    _profil_ancien_compte[instance.pk] = instance.compte_type
