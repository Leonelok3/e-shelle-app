from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from jobs.models import OffreJob, SecteurJob, VilleJob


class Command(BaseCommand):
    help = "Cree les donnees de demonstration pour E-Shelle Jobs."

    def handle(self, *args, **options):
        villes = [
            ("Douala", "Littoral"),
            ("Yaounde", "Centre"),
            ("Bafoussam", "Ouest"),
            ("Bamenda", "Nord-Ouest"),
            ("Garoua", "Nord"),
        ]
        secteurs = [
            "Commerce & vente",
            "Transport & livraison",
            "Restauration",
            "Administration",
            "Informatique",
            "Education",
            "Sante",
            "BTP & artisans",
        ]

        ville_objs = {}
        for ordre, (nom, region) in enumerate(villes):
            ville, _ = VilleJob.objects.get_or_create(nom=nom, defaults={"region": region, "ordre": ordre})
            ville_objs[nom] = ville

        secteur_objs = {}
        for ordre, nom in enumerate(secteurs):
            secteur, _ = SecteurJob.objects.get_or_create(nom=nom, defaults={"ordre": ordre})
            secteur_objs[nom] = secteur

        offres = [
            {
                "titre": "Livreur moto quartier Bonamoussadi",
                "entreprise": "Courses Express Douala",
                "secteur": "Transport & livraison",
                "ville": "Douala",
                "quartier": "Bonamoussadi",
                "type_contrat": OffreJob.TypeContrat.MISSION,
                "salaire_min": 80000,
                "salaire_max": 150000,
                "description": "Nous recherchons des livreurs moto disponibles pour courses locales, repas et petits colis.",
                "profil_recherche": "Moto personnelle, telephone Android, bonne connaissance des quartiers de Douala.",
                "telephone": "+237680625082",
                "whatsapp": "237680625082",
            },
            {
                "titre": "Commercial terrain",
                "entreprise": "E-Shelle Business",
                "secteur": "Commerce & vente",
                "ville": "Yaounde",
                "quartier": "Mvog-Mbi",
                "type_contrat": OffreJob.TypeContrat.CDD,
                "salaire_min": 100000,
                "salaire_max": 250000,
                "description": "Prospection de commerces, restaurants et services locaux pour inscription sur E-Shelle.",
                "profil_recherche": "Aisance relationnelle, discipline, experience vente terrain appreciee.",
                "telephone": "+237680625082",
                "whatsapp": "237680625082",
            },
            {
                "titre": "Stagiaire assistant administratif",
                "entreprise": "Cabinet Partenaire",
                "secteur": "Administration",
                "ville": "Bafoussam",
                "quartier": "Centre-ville",
                "type_contrat": OffreJob.TypeContrat.STAGE,
                "salaire_min": 50000,
                "description": "Accueil, saisie, classement des dossiers et assistance aux operations quotidiennes.",
                "profil_recherche": "Bonne expression francaise, ponctualite, maitrise Word/Excel.",
                "telephone": "+237680625082",
                "whatsapp": "237680625082",
            },
        ]

        count = 0
        for spec in offres:
            defaults = {
                "secteur": secteur_objs[spec.pop("secteur")],
                "ville": ville_objs[spec.pop("ville")],
                "is_active": True,
                "is_verified": True,
                "is_featured": True,
                "date_limite": timezone.localdate() + timedelta(days=30),
                **spec,
            }
            _, created = OffreJob.objects.get_or_create(
                titre=defaults["titre"],
                entreprise=defaults["entreprise"],
                defaults=defaults,
            )
            count += int(created)

        self.stdout.write(self.style.SUCCESS(f"E-Shelle Jobs pret: {count} nouvelle(s) offre(s)."))
