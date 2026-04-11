"""
E-Shelle Resto — Signals
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Restaurant, MenuCategory, ContactLog, Review, Notification


@receiver(post_save, sender=Restaurant)
def create_default_menu_categories(sender, instance, created, **kwargs):
    """Create default menu categories when a new restaurant is created."""
    if created:
        default_categories = [
            ("Plats principaux", 0),
            ("Entrées", 1),
            ("Boissons", 2),
            ("Desserts", 3),
        ]
        for name, order in default_categories:
            MenuCategory.objects.get_or_create(
                restaurant=instance,
                name=name,
                defaults={"order": order},
            )


@receiver(post_save, sender=ContactLog)
def notify_restaurant_on_contact(sender, instance, created, **kwargs):
    """
    Crée une notification interne pour le restaurateur
    à chaque nouveau contact (appel ou WhatsApp).
    """
    if not created:
        return

    if instance.action == "whatsapp":
        notif_type = "contact_whatsapp"
        dish_info = f" pour « {instance.dish.name} »" if instance.dish else ""
        message = (
            f"Nouveau contact WhatsApp{dish_info} sur votre restaurant. "
            f"Un client souhaite passer commande !"
        )
    else:
        notif_type = "contact_call"
        message = (
            f"Nouveau appel téléphonique reçu sur votre restaurant. "
            f"Un client vous a contacté."
        )

    Notification.objects.create(
        restaurant=instance.restaurant,
        type=notif_type,
        message=message,
    )


@receiver(post_save, sender=Review)
def notify_restaurant_on_review(sender, instance, created, **kwargs):
    """Notifie le restaurateur quand un nouvel avis est soumis."""
    if not created:
        return

    stars = "★" * instance.rating + "☆" * (5 - instance.rating)
    message = (
        f"Nouvel avis de {instance.author_name} ({stars}) : "
        f"« {instance.comment[:100]}{'…' if len(instance.comment) > 100 else ''} » "
        f"— En attente de modération."
    )
    Notification.objects.create(
        restaurant=instance.restaurant,
        type="new_review",
        message=message,
    )
