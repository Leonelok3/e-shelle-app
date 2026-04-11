"""
AdGen — Signaux
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="adgen.AdCampaign")
def init_usage_stat(sender, instance, created, **kwargs):
    """Crée les stats utilisateur si elles n'existent pas encore."""
    if created:
        from adgen.models import AdUsageStat
        AdUsageStat.objects.get_or_create(user=instance.user)
