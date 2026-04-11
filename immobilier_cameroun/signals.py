"""
signals.py — immobilier_cameroun
Signaux Django : notifications email, slugs, mise en avant Premium
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


# ─────────────────────────────────────────────────────────────────
# SIGNAL : BIEN — notifications email au changement de statut
# ─────────────────────────────────────────────────────────────────

@receiver(pre_save, sender="immobilier_cameroun.Bien")
def bien_pre_save(sender, instance, **kwargs):
    """Auto-génère le slug si absent."""
    if not instance.slug:
        from .utils import generer_slug_unique
        instance.slug = generer_slug_unique(instance.titre, sender)


@receiver(post_save, sender="immobilier_cameroun.Bien")
def bien_post_save(sender, instance, created, **kwargs):
    """
    Envoie un email de notification au propriétaire :
    - quand le statut passe à PUBLIE
    - quand le statut passe à REFUSE
    """
    from .models import StatutBien
    from .utils import envoyer_email_notification

    if not instance.proprietaire.email:
        return

    if instance.statut == StatutBien.PUBLIE:
        envoyer_email_notification(
            destinataire=instance.proprietaire.email,
            sujet=f"✅ Votre bien « {instance.titre} » a été publié — E-Shelle Immo",
            template_html="immobilier_cameroun/emails/bien_publie.html",
            context={"bien": instance, "user": instance.proprietaire},
        )

    elif instance.statut == StatutBien.REFUSE:
        envoyer_email_notification(
            destinataire=instance.proprietaire.email,
            sujet=f"❌ Votre bien « {instance.titre} » n'a pas été validé — E-Shelle Immo",
            template_html="immobilier_cameroun/emails/bien_refuse.html",
            context={
                "bien": instance,
                "user": instance.proprietaire,
                "note_admin": instance.note_admin,
            },
        )


# ─────────────────────────────────────────────────────────────────
# SIGNAL : DEMANDE DE VISITE — notification propriétaire
# ─────────────────────────────────────────────────────────────────

@receiver(post_save, sender="immobilier_cameroun.DemandeVisite")
def demande_visite_post_save(sender, instance, created, **kwargs):
    """Notifie le propriétaire du bien par email à chaque nouvelle demande."""
    if not created:
        return

    from .utils import envoyer_email_notification

    proprietaire = instance.bien.proprietaire
    if not proprietaire.email:
        return

    envoyer_email_notification(
        destinataire=proprietaire.email,
        sujet=f"📅 Nouvelle demande de visite pour « {instance.bien.titre} »",
        template_html="immobilier_cameroun/emails/demande_visite.html",
        context={"demande": instance, "bien": instance.bien},
    )


# ─────────────────────────────────────────────────────────────────
# SIGNAL : PROFIL IMMO — mise en avant auto quand passage à Premium
# ─────────────────────────────────────────────────────────────────

@receiver(pre_save, sender="immobilier_cameroun.ProfilImmo")
def profil_immo_pre_save(sender, instance, **kwargs):
    """
    Détecte le passage compte_type → PREMIUM et stocke l'ancien statut
    dans un attribut temporaire pour que post_save puisse agir.
    """
    from .models import TypeCompte
    if instance.pk:
        try:
            ancien = sender.objects.get(pk=instance.pk)
            instance._ancien_compte_type = ancien.compte_type
        except sender.DoesNotExist:
            instance._ancien_compte_type = None
    else:
        instance._ancien_compte_type = None


@receiver(post_save, sender="immobilier_cameroun.ProfilImmo")
def profil_immo_post_save(sender, instance, created, **kwargs):
    """
    Quand un utilisateur passe en Premium, tous ses biens publiés
    sont automatiquement mis en avant.
    """
    from .models import TypeCompte, StatutBien

    ancien = getattr(instance, "_ancien_compte_type", None)
    if instance.compte_type == TypeCompte.PREMIUM and ancien != TypeCompte.PREMIUM:
        instance.user.biens_immo.filter(
            statut=StatutBien.PUBLIE
        ).update(est_mis_en_avant=True)
