"""
Signaux Django pour l'app rencontres.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='rencontres.AbonnementRencontre')
def update_profil_premium_status(sender, instance, **kwargs):
    """Met à jour le statut premium du profil lors d'un changement d'abonnement."""
    profil = instance.profil
    is_premium = instance.est_valide()
    if profil.est_premium != is_premium:
        profil.est_premium = is_premium
        profil.save(update_fields=['est_premium'])
