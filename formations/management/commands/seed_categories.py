"""
formations/management/commands/seed_categories.py
Initialise les 4 categories de formations E-Shelle.
Usage : python manage.py seed_categories
"""
from django.core.management.base import BaseCommand
from formations.models import Categorie


CATEGORIES = [
    {
        "nom": "IA & Automatisation",
        "slug": "ia-automatisation",
        "icone": "🤖",
        "ordre": 1,
    },
    {
        "nom": "Marketing Digital",
        "slug": "marketing-digital",
        "icone": "📈",
        "ordre": 2,
    },
    {
        "nom": "Anglais Professionnel",
        "slug": "anglais-professionnel",
        "icone": "🇬🇧",
        "ordre": 3,
    },
    {
        "nom": "Entrepreneuriat Africain",
        "slug": "entrepreneuriat-africain",
        "icone": "🦁",
        "ordre": 4,
    },
]


class Command(BaseCommand):
    help = "Cree les 4 categories de formations E-Shelle"

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for data in CATEGORIES:
            obj, is_new = Categorie.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "nom":    data["nom"],
                    "icone":  data["icone"],
                    "ordre":  data["ordre"],
                    "active": True,
                },
            )
            if is_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  [NEW] {obj.nom}"))
            else:
                updated += 1
                self.stdout.write(f"  [OK]  {obj.nom}")

        self.stdout.write(self.style.SUCCESS(
            f"\nTermine : {created} cree(s), {updated} mis a jour."
        ))
