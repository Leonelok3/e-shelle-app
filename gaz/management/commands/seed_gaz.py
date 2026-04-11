"""
gaz/management/commands/seed_gaz.py
Initialise les donnees de base : villes, quartiers, marques, depots exemples.
Usage : python manage.py seed_gaz
"""
from django.core.management.base import BaseCommand
from gaz.models import VilleGaz, QuartierGaz, MarqueGaz, DepotGaz


VILLES = [
    {"nom": "Yaounde",  "region": "Centre",    "ordre": 1},
    {"nom": "Douala",   "region": "Littoral",  "ordre": 2},
    {"nom": "Bafoussam","region": "Ouest",     "ordre": 3},
    {"nom": "Garoua",   "region": "Nord",      "ordre": 4},
    {"nom": "Bamenda",  "region": "Nord-Ouest","ordre": 5},
    {"nom": "Bertoua",  "region": "Est",       "ordre": 6},
    {"nom": "Ebolowa",  "region": "Sud",       "ordre": 7},
    {"nom": "Ngaoundere","region":"Adamaoua",  "ordre": 8},
]

QUARTIERS = {
    "Yaounde": [
        "Bastos","Omnisports","Nlongkak","Mfandena","Mvog-Ada",
        "Biyem-Assi","Cite Verte","Mendong","Ekounou","Nsimeyong",
        "Essos","Melen","Nkolbisson","Obili","Kondengui",
        "Centre-Ville","Mvog-Mbi","Nkol-Eton","Tongolo","Messa",
    ],
    "Douala": [
        "Akwa","Bonanjo","Bonapriso","Deido","New-Bell",
        "Makepe","Logbessou","Kotto","Ndokotti","Bassa",
        "Bonaberi","PK 14","Ndog-Bong","Yassa","Beedi",
        "Bonamoussadi","Denver","Cité des Palmiers","Logpom","Ndoghem",
    ],
    "Bafoussam": [
        "Centre Commercial","Banengo","Kamkop","Djeleng","Tougang",
        "Famla","Ndiangdam","Tamdja",
    ],
    "Garoua": [
        "Centre-Ville","Plateau","Roumdé Adjia","Marouva","Bocklé",
    ],
    "Bamenda": [
        "Commercial Avenue","Up Station","Old Town","Nkwen","Mile 4",
    ],
}

MARQUES = [
    {"nom": "Total Energies", "couleur": "#E8291D"},
    {"nom": "Tradex",         "couleur": "#00A651"},
    {"nom": "Bocom",          "couleur": "#003087"},
    {"nom": "Victoria",       "couleur": "#FF6B00"},
    {"nom": "Rainbow",        "couleur": "#9B59B6"},
    {"nom": "Gobis",          "couleur": "#F39C12"},
    {"nom": "Nathalie",       "couleur": "#E74C3C"},
    {"nom": "Mvo",            "couleur": "#2ECC71"},
]

# Depots exemples (seront crees uniquement si la table est vide)
DEPOTS_EXEMPLES = [
    {
        "nom": "Depot Gaz Express Bastos",
        "ville": "Yaounde",
        "quartier": "Bastos",
        "telephone": "+237 690 123 456",
        "whatsapp": "237690123456",
        "adresse": "Face au rond-point Bastos, derriere la pharmacie",
        "zone_livraison": "Bastos, Omnisports, Nlongkak, Mfandena, Cite Verte",
        "tailles": ["6kg", "12kg", "15kg"],
        "prix_6kg": 4500,
        "prix_12kg": 8500,
        "prix_15kg": 10500,
        "marques": ["Total Energies", "Tradex"],
        "livraison_rapide": True,
        "delai_livraison": "20-40 min",
        "horaires": "Lun-Dim 6h-22h",
        "livraison_nuit": True,
        "is_featured": True,
        "is_verified": True,
    },
    {
        "nom": "Gaz Service Biyem-Assi",
        "ville": "Yaounde",
        "quartier": "Biyem-Assi",
        "telephone": "+237 677 234 567",
        "whatsapp": "237677234567",
        "adresse": "Carrefour Biyem-Assi, 100m du supermarche Casino",
        "zone_livraison": "Biyem-Assi, Mendong, Nsimeyong, Obili, Ekounou",
        "tailles": ["6kg", "12kg"],
        "prix_6kg": 4200,
        "prix_12kg": 8000,
        "marques": ["Bocom", "Victoria"],
        "livraison_rapide": True,
        "delai_livraison": "30-60 min",
        "horaires": "Lun-Sam 7h-21h",
        "livraison_nuit": False,
        "is_featured": True,
        "is_verified": True,
    },
    {
        "nom": "Depot Central Gaz Akwa",
        "ville": "Douala",
        "quartier": "Akwa",
        "telephone": "+237 699 345 678",
        "whatsapp": "237699345678",
        "adresse": "Boulevard de la Republique, face Hotel Ibis",
        "zone_livraison": "Akwa, Bonanjo, Bonapriso, Deido, Centre-Ville Douala",
        "tailles": ["6kg", "12kg", "15kg", "38kg"],
        "prix_6kg": 4500,
        "prix_12kg": 8800,
        "prix_15kg": 11000,
        "marques": ["Total Energies", "Tradex", "Bocom"],
        "livraison_rapide": True,
        "delai_livraison": "30-45 min",
        "horaires": "Lun-Dim 6h-23h",
        "livraison_nuit": True,
        "is_featured": True,
        "is_verified": True,
    },
    {
        "nom": "Gaz Rapide Makepe",
        "ville": "Douala",
        "quartier": "Makepe",
        "telephone": "+237 655 456 789",
        "whatsapp": "237655456789",
        "adresse": "Carrefour Makepe Missoke",
        "zone_livraison": "Makepe, Logbessou, Kotto, Bonamoussadi",
        "tailles": ["6kg", "12kg"],
        "prix_6kg": 4300,
        "prix_12kg": 8200,
        "marques": ["Rainbow", "Gobis"],
        "livraison_rapide": True,
        "delai_livraison": "30-60 min",
        "horaires": "Lun-Sam 7h-20h",
        "livraison_nuit": False,
        "is_featured": False,
        "is_verified": True,
    },
    {
        "nom": "Gaz & Go Essos",
        "ville": "Yaounde",
        "quartier": "Essos",
        "telephone": "+237 680 567 890",
        "whatsapp": "237680567890",
        "adresse": "Essos carrefour 8eme, pres du marche",
        "zone_livraison": "Essos, Melen, Ekounou, Mvog-Ada",
        "tailles": ["6kg", "12kg", "15kg"],
        "prix_6kg": 4400,
        "prix_12kg": 8300,
        "marques": ["Victoria", "Nathalie"],
        "livraison_rapide": False,
        "delai_livraison": "45-90 min",
        "horaires": "Lun-Sam 7h-19h",
        "livraison_nuit": False,
        "is_featured": False,
        "is_verified": False,
    },
]


class Command(BaseCommand):
    help = "Initialise les donnees E-Shelle Gaz (villes, quartiers, marques, depots demo)"

    def handle(self, *args, **options):
        self.stdout.write("\n=== E-Shelle Gaz — Seed ===\n")

        # Villes
        self.stdout.write("Villes...")
        for data in VILLES:
            obj, created = VilleGaz.objects.get_or_create(
                nom=data["nom"],
                defaults={"region": data["region"], "ordre": data["ordre"], "active": True}
            )
            status = "NEW" if created else "OK "
            self.stdout.write(f"  [{status}] {obj.nom} ({obj.region})")

        # Quartiers
        self.stdout.write("\nQuartiers...")
        for ville_nom, quartiers in QUARTIERS.items():
            try:
                ville = VilleGaz.objects.get(nom=ville_nom)
            except VilleGaz.DoesNotExist:
                continue
            for nom in quartiers:
                _, created = QuartierGaz.objects.get_or_create(
                    ville=ville, nom=nom, defaults={"active": True}
                )
                if created:
                    self.stdout.write(f"  [NEW] {nom} ({ville_nom})")

        # Marques
        self.stdout.write("\nMarques...")
        for data in MARQUES:
            obj, created = MarqueGaz.objects.get_or_create(
                nom=data["nom"],
                defaults={"couleur": data["couleur"], "active": True}
            )
            status = "NEW" if created else "OK "
            self.stdout.write(f"  [{status}] {obj.nom}")

        # Depots exemples
        if DepotGaz.objects.count() == 0:
            self.stdout.write("\nDepots exemples...")
            for data in DEPOTS_EXEMPLES:
                try:
                    ville = VilleGaz.objects.get(nom=data["ville"])
                except VilleGaz.DoesNotExist:
                    continue

                quartier = None
                if data.get("quartier"):
                    quartier = QuartierGaz.objects.filter(
                        ville=ville, nom=data["quartier"]
                    ).first()

                depot = DepotGaz.objects.create(
                    nom=data["nom"],
                    ville=ville,
                    quartier=quartier,
                    telephone=data["telephone"],
                    whatsapp=data.get("whatsapp", ""),
                    adresse=data.get("adresse", ""),
                    zone_livraison=data.get("zone_livraison", ""),
                    tailles=data.get("tailles", []),
                    prix_6kg=data.get("prix_6kg"),
                    prix_12kg=data.get("prix_12kg"),
                    prix_15kg=data.get("prix_15kg"),
                    livraison_rapide=data.get("livraison_rapide", True),
                    delai_livraison=data.get("delai_livraison", "30-60 min"),
                    horaires=data.get("horaires", "Lun-Sam 7h-20h"),
                    livraison_nuit=data.get("livraison_nuit", False),
                    is_featured=data.get("is_featured", False),
                    is_verified=data.get("is_verified", False),
                    is_active=True,
                )
                # Marques
                for marque_nom in data.get("marques", []):
                    try:
                        depot.marques.add(MarqueGaz.objects.get(nom=marque_nom))
                    except MarqueGaz.DoesNotExist:
                        pass

                self.stdout.write(f"  [NEW] {depot.nom}")
        else:
            self.stdout.write(f"\n[INFO] {DepotGaz.objects.count()} depots existants — seed des depots skipped.")

        self.stdout.write(self.style.SUCCESS("\nSeed termine avec succes !"))
