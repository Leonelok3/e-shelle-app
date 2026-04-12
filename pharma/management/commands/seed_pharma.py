"""
pharma/management/commands/seed_pharma.py
Initialise les données de base : villes, quartiers, catégories, médicaments, pharmacies démo.
Usage : python manage.py seed_pharma
"""
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from pharma.models import (VillePharma, QuartierPharma, CategorieMedicament,
                            Medicament, Pharmacie, StockPharmacie)


VILLES = [
    {"nom": "Yaoundé",    "region": "Centre",    "ordre": 1},
    {"nom": "Douala",     "region": "Littoral",  "ordre": 2},
    {"nom": "Bafoussam",  "region": "Ouest",     "ordre": 3},
    {"nom": "Garoua",     "region": "Nord",      "ordre": 4},
    {"nom": "Bamenda",    "region": "Nord-Ouest","ordre": 5},
    {"nom": "Bertoua",    "region": "Est",       "ordre": 6},
    {"nom": "Ebolowa",    "region": "Sud",       "ordre": 7},
    {"nom": "Ngaoundéré", "region": "Adamaoua",  "ordre": 8},
]

QUARTIERS = {
    "Yaoundé": [
        "Bastos","Omnisports","Nlongkak","Mfandena","Mvog-Ada",
        "Biyem-Assi","Cité Verte","Mendong","Ekounou","Nsimeyong",
        "Essos","Melen","Nkolbisson","Obili","Centre-Ville",
        "Mvog-Mbi","Nkol-Eton","Tongolo","Messa","Kondengui",
    ],
    "Douala": [
        "Akwa","Bonanjo","Bonapriso","Deido","New-Bell",
        "Makepe","Logbessou","Kotto","Ndokotti","Bassa",
        "Bonaberi","Bonamoussadi","Logpom","Ndoghem","Yassa",
    ],
    "Bafoussam": [
        "Centre Commercial","Banengo","Kamkop","Djeleng","Tougang",
    ],
    "Garoua": [
        "Centre-Ville","Plateau","Roumdé Adjia","Marouva",
    ],
    "Bamenda": [
        "Commercial Avenue","Up Station","Old Town","Nkwen","Mile 4",
    ],
}

CATEGORIES = [
    {"nom": "Antipaludéens",      "icone": "🦟", "ordre": 1},
    {"nom": "Antibiotiques",      "icone": "🦠", "ordre": 2},
    {"nom": "Antidouleurs",       "icone": "💊", "ordre": 3},
    {"nom": "Vitamines & Compléments", "icone": "🌿", "ordre": 4},
    {"nom": "Antihypertenseurs",  "icone": "❤️", "ordre": 5},
    {"nom": "Antidiabétiques",    "icone": "🩸", "ordre": 6},
    {"nom": "Antiparasitaires",   "icone": "🐛", "ordre": 7},
    {"nom": "Antiseptiques",      "icone": "🧴", "ordre": 8},
    {"nom": "Gastro-intestinaux", "icone": "🤢", "ordre": 9},
    {"nom": "Pédiatrie",          "icone": "👶", "ordre": 10},
    {"nom": "Dermatologie",       "icone": "🧴", "ordre": 11},
    {"nom": "Ophtalmologie",      "icone": "👁️", "ordre": 12},
]

MEDICAMENTS = [
    # Antipaludéens
    {"nom": "Arthémether-Luméfantrine (Coartem)", "cat": "Antipaludéens", "ordonnance": False},
    {"nom": "Artemisinine",                        "cat": "Antipaludéens", "ordonnance": False},
    {"nom": "Quinine 500mg",                       "cat": "Antipaludéens", "ordonnance": True},
    {"nom": "Chloroquine 250mg",                   "cat": "Antipaludéens", "ordonnance": False},
    {"nom": "Fansidar (SP)",                       "cat": "Antipaludéens", "ordonnance": False},
    # Antibiotiques
    {"nom": "Amoxicilline 500mg",  "cat": "Antibiotiques", "ordonnance": True},
    {"nom": "Azithromycine 500mg", "cat": "Antibiotiques", "ordonnance": True},
    {"nom": "Ciprofloxacine 500mg","cat": "Antibiotiques", "ordonnance": True},
    {"nom": "Doxycycline 100mg",   "cat": "Antibiotiques", "ordonnance": True},
    {"nom": "Métronidazole 250mg", "cat": "Antibiotiques", "ordonnance": False},
    # Antidouleurs
    {"nom": "Paracétamol 500mg",   "cat": "Antidouleurs", "ordonnance": False},
    {"nom": "Ibuprofène 400mg",    "cat": "Antidouleurs", "ordonnance": False},
    {"nom": "Diclofénac 50mg",     "cat": "Antidouleurs", "ordonnance": False},
    {"nom": "Tramadol 100mg",      "cat": "Antidouleurs", "ordonnance": True},
    {"nom": "Aspirine 500mg",      "cat": "Antidouleurs", "ordonnance": False},
    # Vitamines
    {"nom": "Vitamine C 500mg",          "cat": "Vitamines & Compléments", "ordonnance": False},
    {"nom": "Vitamine D3 1000 UI",       "cat": "Vitamines & Compléments", "ordonnance": False},
    {"nom": "Zinc 20mg",                 "cat": "Vitamines & Compléments", "ordonnance": False},
    {"nom": "Fer + Acide folique",       "cat": "Vitamines & Compléments", "ordonnance": False},
    {"nom": "Multivitamines adulte",     "cat": "Vitamines & Compléments", "ordonnance": False},
    # Antihypertenseurs
    {"nom": "Amlodipine 5mg",      "cat": "Antihypertenseurs", "ordonnance": True},
    {"nom": "Losartan 50mg",       "cat": "Antihypertenseurs", "ordonnance": True},
    {"nom": "Captopril 25mg",      "cat": "Antihypertenseurs", "ordonnance": True},
    # Antidiabétiques
    {"nom": "Metformine 500mg",    "cat": "Antidiabétiques", "ordonnance": True},
    {"nom": "Glibenclamide 5mg",   "cat": "Antidiabétiques", "ordonnance": True},
    # Gastro
    {"nom": "Oméprazole 20mg",     "cat": "Gastro-intestinaux", "ordonnance": False},
    {"nom": "Métoclopramide 10mg", "cat": "Gastro-intestinaux", "ordonnance": False},
    {"nom": "SRO (Sels de réhydratation)", "cat": "Gastro-intestinaux", "ordonnance": False},
    {"nom": "Cotrimoxazole 480mg", "cat": "Antibiotiques", "ordonnance": False},
    # Pédiatrie
    {"nom": "Paracétamol sirop 120mg/5ml","cat": "Pédiatrie", "ordonnance": False},
    {"nom": "Amoxicilline sirop 250mg/5ml","cat": "Pédiatrie", "ordonnance": True},
    {"nom": "Fer sirop pédiatrique",       "cat": "Pédiatrie", "ordonnance": False},
    # Antiseptiques
    {"nom": "Alcool iodé 70°",     "cat": "Antiseptiques", "ordonnance": False},
    {"nom": "Bétadine solution",   "cat": "Antiseptiques", "ordonnance": False},
    # Dermatologie
    {"nom": "Bétaméthasone crème", "cat": "Dermatologie", "ordonnance": True},
    {"nom": "Kétoconazole crème",  "cat": "Dermatologie", "ordonnance": False},
    # Antiparasitaires
    {"nom": "Mébendazole 500mg",   "cat": "Antiparasitaires", "ordonnance": False},
    {"nom": "Albendazole 400mg",   "cat": "Antiparasitaires", "ordonnance": False},
]

PHARMACIES_DEMO = [
    {
        "nom": "Pharmacie du Centre Bastos",
        "ville": "Yaoundé", "quartier": "Bastos",
        "telephone": "+237 222 123 456", "whatsapp": "237680123456",
        "adresse": "Avenue de l'Indépendance, face à l'ambassade de France",
        "horaires": "Lun-Dim 7h-22h",
        "garde": True, "garde_info": "De garde cette semaine",
        "livraison": True, "delai_livraison": "30-60 min",
        "plan": "premium", "featured": True, "verified": True,
        "medicaments": [
            ("Paracétamol 500mg", 300), ("Amoxicilline 500mg", 2500),
            ("Arthémether-Luméfantrine (Coartem)", 3500), ("Vitamine C 500mg", 500),
            ("Oméprazole 20mg", 800), ("Ibuprofène 400mg", 400),
            ("Métronidazole 250mg", 600), ("Zinc 20mg", 350),
        ],
    },
    {
        "nom": "Grande Pharmacie Biyem-Assi",
        "ville": "Yaoundé", "quartier": "Biyem-Assi",
        "telephone": "+237 677 234 567", "whatsapp": "237677234567",
        "adresse": "Carrefour Biyem-Assi, 50m du supermarché Casino",
        "horaires": "Lun-Sam 7h30-21h",
        "garde": False, "livraison": False,
        "plan": "pro", "featured": True, "verified": True,
        "medicaments": [
            ("Paracétamol 500mg", 300), ("Ibuprofène 400mg", 400),
            ("Aspirin 500mg", 250), ("Chloroquine 250mg", 600),
            ("SRO (Sels de réhydratation)", 200), ("Bétadine solution", 1500),
            ("Mébendazole 500mg", 800), ("Fer + Acide folique", 700),
        ],
    },
    {
        "nom": "Pharmacie Centrale Akwa",
        "ville": "Douala", "quartier": "Akwa",
        "telephone": "+237 233 345 678", "whatsapp": "237699345678",
        "adresse": "Boulevard de la République, face Hôtel Ibis",
        "horaires": "Lun-Dim 7h-23h",
        "garde": True, "garde_info": "Garde permanente 24h/24",
        "livraison": True, "delai_livraison": "20-45 min",
        "plan": "premium", "featured": True, "verified": True,
        "medicaments": [
            ("Paracétamol 500mg", 300), ("Amoxicilline 500mg", 2500),
            ("Arthémether-Luméfantrine (Coartem)", 3500), ("Quinine 500mg", 1500),
            ("Metformine 500mg", 900), ("Amlodipine 5mg", 1200),
            ("Azithromycine 500mg", 3000), ("Ciprofloxacine 500mg", 2800),
            ("Vitamine C 500mg", 500), ("Multivitamines adulte", 2500),
        ],
    },
    {
        "nom": "Pharmacie Makepe Santé",
        "ville": "Douala", "quartier": "Makepe",
        "telephone": "+237 655 456 789", "whatsapp": "237655456789",
        "adresse": "Carrefour Makepe Missoke, rue principale",
        "horaires": "Lun-Sam 7h-20h",
        "garde": False, "livraison": False,
        "plan": "basic", "featured": False, "verified": True,
        "medicaments": [
            ("Paracétamol 500mg", 300), ("Chloroquine 250mg", 600),
            ("SRO (Sels de réhydratation)", 200), ("Alcool iodé 70°", 800),
            ("Paracétamol sirop 120mg/5ml", 1500), ("Albendazole 400mg", 700),
        ],
    },
    {
        "nom": "Pharmacie Essos Plus",
        "ville": "Yaoundé", "quartier": "Essos",
        "telephone": "+237 680 567 890", "whatsapp": "237680567890",
        "adresse": "Essos carrefour 8ème, à côté du marché",
        "horaires": "Lun-Sam 7h30-20h30",
        "garde": False, "livraison": True, "delai_livraison": "45-90 min",
        "plan": "pro", "featured": False, "verified": False,
        "medicaments": [
            ("Paracétamol 500mg", 300), ("Ibuprofène 400mg", 400),
            ("Vitamine D3 1000 UI", 1200), ("Zinc 20mg", 350),
            ("Fansidar (SP)", 800), ("Doxycycline 100mg", 1800),
        ],
    },
]


class Command(BaseCommand):
    help = "Initialise les données E-Shelle Pharma (villes, catégories, médicaments, pharmacies démo)"

    def handle(self, *args, **options):
        self.stdout.write("\n=== E-Shelle Pharma — Seed ===\n")

        # Villes
        self.stdout.write("Villes...")
        for data in VILLES:
            obj, created = VillePharma.objects.get_or_create(
                nom=data["nom"],
                defaults={"region": data["region"], "ordre": data["ordre"], "active": True}
            )
            self.stdout.write(f"  [{'NEW' if created else 'OK '}] {obj.nom}")

        # Quartiers
        self.stdout.write("\nQuartiers...")
        for ville_nom, quartiers in QUARTIERS.items():
            try:
                ville = VillePharma.objects.get(nom=ville_nom)
            except VillePharma.DoesNotExist:
                continue
            for nom in quartiers:
                _, created = QuartierPharma.objects.get_or_create(
                    ville=ville, nom=nom, defaults={"active": True}
                )
                if created:
                    self.stdout.write(f"  [NEW] {nom} ({ville_nom})")

        # Catégories
        self.stdout.write("\nCatégories...")
        for data in CATEGORIES:
            obj, created = CategorieMedicament.objects.get_or_create(
                nom=data["nom"],
                defaults={"icone": data["icone"], "ordre": data["ordre"], "active": True}
            )
            self.stdout.write(f"  [{'NEW' if created else 'OK '}] {obj.nom}")

        # Médicaments
        self.stdout.write("\nMédicaments...")
        for data in MEDICAMENTS:
            try:
                cat = CategorieMedicament.objects.get(nom=data["cat"])
            except CategorieMedicament.DoesNotExist:
                cat = None
            obj, created = Medicament.objects.get_or_create(
                nom=data["nom"],
                defaults={"categorie": cat, "ordonnance": data.get("ordonnance", False), "actif": True}
            )
            if created:
                self.stdout.write(f"  [NEW] {obj.nom}")

        # Pharmacies démo
        if Pharmacie.objects.count() == 0:
            self.stdout.write("\nPharmacies démo...")
            for data in PHARMACIES_DEMO:
                try:
                    ville = VillePharma.objects.get(nom=data["ville"])
                except VillePharma.DoesNotExist:
                    continue

                quartier = QuartierPharma.objects.filter(
                    ville=ville, nom=data.get("quartier", "")
                ).first()

                pharmacie = Pharmacie.objects.create(
                    nom=data["nom"],
                    ville=ville,
                    quartier=quartier,
                    telephone=data["telephone"],
                    whatsapp=data.get("whatsapp", ""),
                    adresse=data.get("adresse", ""),
                    horaires=data.get("horaires", "Lun-Sam 8h-20h"),
                    garde=data.get("garde", False),
                    garde_info=data.get("garde_info", ""),
                    livraison=data.get("livraison", False),
                    delai_livraison=data.get("delai_livraison", ""),
                    is_active=True,
                    abonnement_actif=True,
                    plan_actif=data.get("plan", "pro"),
                    abonnement_expire_le=date.today() + timedelta(days=30),
                    montant_paye={"basic": 2000, "pro": 5000, "premium": 10000}.get(data.get("plan", "pro"), 5000),
                    notes_admin="Pharmacie démo créée par seed_pharma",
                    is_featured=data.get("featured", False),
                    is_verified=data.get("verified", False),
                )

                # Stocks
                for med_nom, prix in data.get("medicaments", []):
                    try:
                        med = Medicament.objects.get(nom=med_nom)
                        StockPharmacie.objects.create(
                            pharmacie=pharmacie, medicament=med,
                            prix=prix, disponible=True
                        )
                    except Medicament.DoesNotExist:
                        pass

                self.stdout.write(f"  [NEW] {pharmacie.nom} ({len(data.get('medicaments', []))} médicaments)")
        else:
            count = Pharmacie.objects.count()
            self.stdout.write(f"\n[INFO] {count} pharmacie(s) existante(s) — seed pharmacies skipped.")

        self.stdout.write(self.style.SUCCESS("\nSeed terminé avec succès !"))
