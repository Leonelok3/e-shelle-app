from datetime import time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from transport_core.models import Trajet, VilleTransport


class Command(BaseCommand):
    help = "Cree les villes et trajets de demo pour E-Shelle Transport."

    def handle(self, *args, **options):
        villes_data = [
            ("Douala", "Littoral"),
            ("Yaounde", "Centre"),
            ("Bafoussam", "Ouest"),
            ("Bamenda", "Nord-Ouest"),
            ("Garoua", "Nord"),
            ("Kribi", "Sud"),
            ("Buea", "Sud-Ouest"),
            ("Limbe", "Sud-Ouest"),
        ]
        villes = {}
        for ordre, (nom, region) in enumerate(villes_data, start=1):
            ville, _ = VilleTransport.objects.update_or_create(
                nom=nom,
                defaults={"region": region, "active": True, "ordre": ordre},
            )
            villes[nom] = ville

        today = timezone.localdate()
        trajets = [
            {
                "titre": "Covoiturage confortable Douala vers Yaounde",
                "type_trajet": Trajet.TypeTrajet.COVOITURAGE,
                "depart": villes["Douala"],
                "arrivee": villes["Yaounde"],
                "lieu_depart": "Bonaberi, Total Ndogpassi",
                "lieu_arrivee": "Mvan, Yaounde",
                "date_depart": today + timedelta(days=1),
                "heure_depart": time(7, 30),
                "places_disponibles": 3,
                "prix_place": 6000,
                "conducteur_nom": "Cedric M.",
                "telephone": "+237680625082",
                "whatsapp": "237680625082",
                "vehicule": "Toyota Corolla climatisée",
                "bagages_acceptes": True,
                "colis_acceptes": True,
                "description": "Départ ponctuel, trajet direct avec arrêt court à Edéa.",
                "conditions": "Réservation confirmée par appel ou WhatsApp.",
                "is_featured": True,
            },
            {
                "titre": "Bus VIP Yaounde vers Bafoussam",
                "type_trajet": Trajet.TypeTrajet.BUS,
                "depart": villes["Yaounde"],
                "arrivee": villes["Bafoussam"],
                "lieu_depart": "Agence Mvan",
                "lieu_arrivee": "Entrée ville Bafoussam",
                "date_depart": today + timedelta(days=2),
                "heure_depart": time(9, 0),
                "places_disponibles": 12,
                "prix_place": 5000,
                "conducteur_nom": "Agence Partenaire",
                "telephone": "+237680625082",
                "whatsapp": "237680625082",
                "vehicule": "Bus VIP 30 places",
                "bagages_acceptes": True,
                "colis_acceptes": True,
                "description": "Places limitées avec départ en matinée.",
                "conditions": "Arriver 30 minutes avant le départ.",
                "is_featured": True,
            },
            {
                "titre": "Douala vers Kribi avec place bagages",
                "type_trajet": Trajet.TypeTrajet.COVOITURAGE,
                "depart": villes["Douala"],
                "arrivee": villes["Kribi"],
                "lieu_depart": "Carrefour Yassa",
                "lieu_arrivee": "Centre-ville Kribi",
                "date_depart": today + timedelta(days=3),
                "heure_depart": time(6, 45),
                "places_disponibles": 2,
                "prix_place": 4500,
                "conducteur_nom": "Ariane T.",
                "telephone": "+237680625082",
                "whatsapp": "237680625082",
                "vehicule": "SUV familial",
                "bagages_acceptes": True,
                "colis_acceptes": False,
                "description": "Trajet calme, idéal pour weekend ou déplacement pro.",
                "conditions": "Bagage moyen par passager.",
                "is_featured": False,
            },
            {
                "titre": "Buea vers Douala matin",
                "type_trajet": Trajet.TypeTrajet.TAXI,
                "depart": villes["Buea"],
                "arrivee": villes["Douala"],
                "lieu_depart": "Molyko",
                "lieu_arrivee": "Bonamoussadi",
                "date_depart": today + timedelta(days=1),
                "heure_depart": time(8, 15),
                "places_disponibles": 4,
                "prix_place": 4000,
                "conducteur_nom": "Patrick N.",
                "telephone": "+237680625082",
                "whatsapp": "237680625082",
                "vehicule": "Taxi interurbain",
                "bagages_acceptes": True,
                "colis_acceptes": True,
                "description": "Départ groupé depuis Molyko, arrivée côté Bonamoussadi.",
                "conditions": "Paiement direct au conducteur.",
                "is_featured": False,
            },
        ]

        created = 0
        for data in trajets:
            trajet, was_created = Trajet.objects.update_or_create(
                titre=data["titre"],
                depart=data["depart"],
                arrivee=data["arrivee"],
                date_depart=data["date_depart"],
                defaults={
                    **data,
                    "is_active": True,
                    "is_verified": True,
                    "statut": Trajet.Statut.OUVERT,
                },
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(f"E-Shelle Transport pret: {created} nouveau(x) trajet(s)."))
