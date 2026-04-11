"""
python manage.py adgen_init_modules
Initialise les modules AdGen par défaut en base de données.
"""
from django.core.management.base import BaseCommand
from adgen.models import AdModule

DEFAULT_MODULES = [
    {
        "slug": "titres",
        "name": "Titres accrocheurs",
        "description": "3 titres marketing percutants pour attirer l'attention",
        "icon": "🎯",
        "is_active": True,
        "is_premium": False,
        "order": 1,
    },
    {
        "slug": "description",
        "name": "Description & bénéfices",
        "description": "Texte de vente + liste de 5 bénéfices clients",
        "icon": "📝",
        "is_active": True,
        "is_premium": False,
        "order": 2,
    },
    {
        "slug": "social",
        "name": "Posts réseaux sociaux",
        "description": "Facebook, Instagram, WhatsApp + 10 hashtags",
        "icon": "📱",
        "is_active": True,
        "is_premium": False,
        "order": 3,
    },
    {
        "slug": "tiktok",
        "name": "Script TikTok",
        "description": "Script vidéo 20 secondes : hook + avantages + CTA",
        "icon": "🎬",
        "is_active": True,
        "is_premium": True,
        "order": 4,
    },
    {
        "slug": "chatbot",
        "name": "Réponse chatbot vendeur",
        "description": "Réponse naturelle d'un vendeur orientée achat",
        "icon": "🤖",
        "is_active": True,
        "is_premium": True,
        "order": 5,
    },
]


class Command(BaseCommand):
    help = "Initialise les modules AdGen par défaut"

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for data in DEFAULT_MODULES:
            obj, is_new = AdModule.objects.update_or_create(
                slug=data["slug"],
                defaults=data,
            )
            if is_new:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"AdGen modules: {created} crees, {updated} mis a jour."
        ))
