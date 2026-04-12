"""seed_pressing.py — Données de démonstration E-Shelle Pressing"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = "Insère des données de démonstration pour E-Shelle Pressing"

    def handle(self, *args, **options):
        from pressing.models import (
            VillePressing, QuartierPressing, CategoriePressing,
            Pressing, ServicePressing
        )

        self.stdout.write("\n=== E-Shelle Pressing — Seed ===\n")

        # ── VILLES ─────────────────────────────────────────────────────────
        villes_data = [
            ("Yaoundé",    "yaounde"),
            ("Douala",     "douala"),
            ("Bafoussam",  "bafoussam"),
            ("Buea",       "buea"),
            ("Limbe",      "limbe"),
            ("Bamenda",    "bamenda"),
            ("Garoua",     "garoua"),
            ("Maroua",     "maroua"),
        ]
        villes = {}
        for nom, slug in villes_data:
            v, c = VillePressing.objects.get_or_create(slug=slug, defaults={"nom": nom})
            villes[slug] = v
            self.stdout.write(f"  {'[NEW]' if c else '[OK ]'} Ville: {nom}")

        # ── QUARTIERS ──────────────────────────────────────────────────────
        quartiers_data = {
            "yaounde": [
                "Bastos", "Nlongkak", "Mfoundi", "Melen", "Essos",
                "Mvog-Mbi", "Obili", "Nkomo", "Centre-ville", "Biyem-Assi",
                "Mimboman", "Nkolbisson", "Mendong", "Tsinga",
            ],
            "douala": [
                "Akwa", "Bonanjo", "Deido", "Bali", "Bonaberi",
                "Makepe", "Logpom", "Kotto", "Ndokotti", "Bonapriso",
                "Bepanda", "PK8", "Ndog-Bong",
            ],
            "bafoussam": [
                "Centre", "Tamdja", "Kamkop", "Djeleng", "Galim",
            ],
            "buea": ["Molyko", "Mile 16", "Bokwango", "Bonduma"],
            "limbe": ["Down Beach", "New Town", "Mile 2"],
            "bamenda": ["Commercial Avenue", "Nkwen", "Old Town", "Mankon"],
            "garoua": ["Centre", "Poumpoumre", "Roumdé Adjia"],
            "maroua": ["Centre", "Dougoy", "Domayo"],
        }
        quartiers = {}
        for ville_slug, qrts in quartiers_data.items():
            ville = villes[ville_slug]
            for nom in qrts:
                q, c = QuartierPressing.objects.get_or_create(
                    ville=ville,
                    nom=nom,
                    defaults={"slug": f"{ville_slug}-{nom.lower().replace(' ', '-').replace("'", '')}"}
                )
                quartiers[f"{ville_slug}_{nom}"] = q

        # ── CATEGORIES ─────────────────────────────────────────────────────
        cats_data = [
            ("Pressing",        "pressing",       "👔"),
            ("Blanchisserie",   "blanchisserie",  "🧺"),
            ("Teinturerie",     "teinturerie",    "🎨"),
            ("Cuir & Maroquin", "cuir",           "👜"),
        ]
        cats = {}
        for nom, slug, icone in cats_data:
            cat, c = CategoriePressing.objects.get_or_create(
                slug=slug, defaults={"nom": nom, "icone": icone}
            )
            cats[slug] = cat
            self.stdout.write(f"  {'[NEW]' if c else '[OK ]'} Categorie: {nom}")

        # ── PRESSINGS ─────────────────────────────────────────────────────
        expire = timezone.now().date() + timedelta(days=90)

        pressings_data = [
            # Yaoundé
            {
                "nom": "Pressing Imperial",
                "slug": "pressing-imperial-yaounde",
                "ville": "yaounde",
                "quartier": "Bastos",
                "adresse": "Rue de Nachtigal, Bastos",
                "telephone": "+237 699 100 001",
                "description": "Le pressing haut de gamme de Bastos — vêtements de luxe traités avec soin depuis 2010.",
                "horaires": "Lun–Sam 8h–20h",
                "delai_traitement": "24h",
                "collecte_domicile": True,
                "livraison_domicile": True,
                "express": True,
                "plan_actif": "premium",
                "is_featured": True,
                "is_verified": True,
                "categories": ["pressing", "blanchisserie", "teinturerie"],
            },
            {
                "nom": "Clean & Co Nlongkak",
                "slug": "clean-co-nlongkak",
                "ville": "yaounde",
                "quartier": "Nlongkak",
                "adresse": "Avenue Foch, Nlongkak",
                "telephone": "+237 699 100 002",
                "description": "Pressing moderne avec équipement professionnel et livraison express.",
                "horaires": "Lun–Sam 8h–19h",
                "delai_traitement": "48h",
                "collecte_domicile": True,
                "livraison_domicile": False,
                "express": False,
                "plan_actif": "pro",
                "is_featured": True,
                "is_verified": True,
                "categories": ["pressing", "blanchisserie"],
            },
            {
                "nom": "Pressing Élégance Melen",
                "slug": "pressing-elegance-melen",
                "ville": "yaounde",
                "quartier": "Melen",
                "adresse": "Carrefour Melen",
                "telephone": "+237 677 200 003",
                "description": "Soin expert de vos vêtements, linge de maison et cuirs.",
                "horaires": "Lun–Sam 7h30–19h30",
                "delai_traitement": "48h",
                "collecte_domicile": False,
                "livraison_domicile": False,
                "express": False,
                "plan_actif": "basic",
                "is_featured": False,
                "is_verified": True,
                "categories": ["pressing", "teinturerie"],
            },
            {
                "nom": "Prestige Pressing Biyem-Assi",
                "slug": "prestige-pressing-biyem-assi",
                "ville": "yaounde",
                "quartier": "Biyem-Assi",
                "adresse": "Marché Biyem-Assi",
                "telephone": "+237 656 300 004",
                "description": "Vos vêtements méritent le meilleur — qualité garantie.",
                "horaires": "Lun–Dim 8h–20h",
                "delai_traitement": "24h",
                "collecte_domicile": True,
                "livraison_domicile": True,
                "express": True,
                "plan_actif": "pro",
                "is_featured": False,
                "is_verified": False,
                "categories": ["pressing", "blanchisserie", "cuir"],
            },
            # Douala
            {
                "nom": "Royal Pressing Akwa",
                "slug": "royal-pressing-akwa",
                "ville": "douala",
                "quartier": "Akwa",
                "adresse": "Boulevard de la Liberté, Akwa",
                "telephone": "+237 699 400 005",
                "description": "Leader du pressing à Douala depuis 2008. Vêtements de soirée, costumes, robes de mariée.",
                "horaires": "Lun–Sam 7h–20h",
                "delai_traitement": "24h",
                "collecte_domicile": True,
                "livraison_domicile": True,
                "express": True,
                "plan_actif": "premium",
                "is_featured": True,
                "is_verified": True,
                "categories": ["pressing", "blanchisserie", "teinturerie", "cuir"],
            },
            {
                "nom": "Blanchisserie Centrale Bonanjo",
                "slug": "blanchisserie-centrale-bonanjo",
                "ville": "douala",
                "quartier": "Bonanjo",
                "adresse": "Rue du Commerce, Bonanjo",
                "telephone": "+237 677 500 006",
                "description": "Spécialiste linge de maison, hôtels et restaurants.",
                "horaires": "Lun–Sam 8h–18h",
                "delai_traitement": "72h",
                "collecte_domicile": True,
                "livraison_domicile": True,
                "express": False,
                "plan_actif": "pro",
                "is_featured": True,
                "is_verified": True,
                "categories": ["blanchisserie"],
            },
            {
                "nom": "Flash Pressing Makepe",
                "slug": "flash-pressing-makepe",
                "ville": "douala",
                "quartier": "Makepe",
                "adresse": "Carrefour Makepe Missoke",
                "telephone": "+237 656 600 007",
                "description": "Service rapide et fiable dans le quartier de Makepe.",
                "horaires": "Lun–Sam 7h–19h30",
                "delai_traitement": "24h",
                "collecte_domicile": False,
                "livraison_domicile": False,
                "express": True,
                "plan_actif": "basic",
                "is_featured": False,
                "is_verified": False,
                "categories": ["pressing"],
            },
            # Bafoussam
            {
                "nom": "Pressing Victoria Bafoussam",
                "slug": "pressing-victoria-bafoussam",
                "ville": "bafoussam",
                "quartier": "Centre",
                "adresse": "Marché A, Centre-ville Bafoussam",
                "telephone": "+237 699 700 008",
                "description": "Le pressing de référence des hauts-plateaux.",
                "horaires": "Lun–Sam 8h–18h",
                "delai_traitement": "48h",
                "collecte_domicile": False,
                "livraison_domicile": False,
                "express": False,
                "plan_actif": "basic",
                "is_featured": False,
                "is_verified": True,
                "categories": ["pressing", "blanchisserie"],
            },
        ]

        # Tarifs par catégorie
        services_templates = {
            "pressing": [
                ("Chemise homme",   "chemise_h",    "👔", 500,  "piece"),
                ("Pantalon",        "pantalon",     "👖", 700,  "piece"),
                ("Costume 2 pièces","costume_2p",   "🤵", 2500, "piece"),
                ("Costume 3 pièces","costume_3p",   "🕴", 3200, "piece"),
                ("Robe simple",     "robe_simple",  "👗", 1200, "piece"),
                ("Robe de soirée",  "robe_soiree",  "👘", 3500, "piece"),
                ("Veste",           "veste",        "🧥", 1500, "piece"),
                ("Jupe",            "jupe",         "👗", 800,  "piece"),
                ("Cravate",         "cravate",      "👔", 300,  "piece"),
                ("Burnous / Grand boubou", "boubou", "🪬", 2000, "piece"),
            ],
            "blanchisserie": [
                ("Drap 2 places",   "drap_2p",      "🛏", 1000, "piece"),
                ("Drap 1 place",    "drap_1p",      "🛏", 700,  "piece"),
                ("Couette",         "couette",      "🛏", 2500, "piece"),
                ("Oreillers (2)",   "oreillers",    "🛏", 600,  "piece"),
                ("Serviette bain",  "serviette_b",  "🚿", 500,  "piece"),
                ("Nappe",           "nappe",        "🍽", 1200, "piece"),
                ("Linge au kg",     "linge_kg",     "⚖", 800,  "kg"),
            ],
            "teinturerie": [
                ("Teinture vêtement", "teinture_vet", "🎨", 2500, "piece"),
                ("Décoloration",    "decoloration", "🪣", 3000,  "piece"),
                ("Traitement cuir", "traitement_c", "🧴", 4000,  "piece"),
            ],
            "cuir": [
                ("Sac à main",      "sac_main",     "👜", 2000, "piece"),
                ("Ceinture",        "ceinture",     "🔗", 800,  "piece"),
                ("Chaussures (la paire)", "chaussures", "👞", 1500, "piece"),
                ("Veste en cuir",   "veste_cuir",   "🧥", 4500, "piece"),
            ],
        }

        for pdata in pressings_data:
            ville = villes[pdata["ville"]]
            qkey = f"{pdata['ville']}_{pdata['quartier']}"
            quartier = quartiers.get(qkey)

            p, created = Pressing.objects.get_or_create(
                slug=pdata["slug"],
                defaults={
                    "nom": pdata["nom"],
                    "ville": ville,
                    "quartier": quartier,
                    "adresse": pdata["adresse"],
                    "telephone": pdata["telephone"],
                    "description": pdata["description"],
                    "horaires": pdata["horaires"],
                    "delai_traitement": pdata["delai_traitement"],
                    "collecte_domicile": pdata["collecte_domicile"],
                    "livraison_domicile": pdata["livraison_domicile"],
                    "express": pdata["express"],
                    "is_active": True,
                    "is_featured": pdata["is_featured"],
                    "is_verified": pdata["is_verified"],
                    "plan_actif": pdata["plan_actif"],
                    "abonnement_actif": True,
                    "abonnement_expire_le": expire,
                }
            )
            # Catégories
            for cat_slug in pdata["categories"]:
                p.categories.add(cats[cat_slug])

            # Services
            for cat_slug in pdata["categories"]:
                cat = cats[cat_slug]
                for nom, slug_svc, icone, prix_base, unite in services_templates.get(cat_slug, []):
                    prix = prix_base + random.choice([-100, 0, 100, 200])
                    ServicePressing.objects.get_or_create(
                        pressing=p,
                        nom=nom,
                        defaults={
                            "categorie": cat,
                            "icone": icone,
                            "prix": max(200, prix),
                            "unite": unite,
                            "disponible": True,
                        }
                    )

            self.stdout.write(f"  {'[NEW]' if created else '[OK ]'} Pressing: {pdata['nom']}")

        nb_pressings = Pressing.objects.count()
        nb_services = ServicePressing.objects.count()
        self.stdout.write(f"\n  Total: {nb_pressings} pressings, {nb_services} services\n")
        self.stdout.write("  Seed pressing termine avec succes !\n")
