"""
python manage.py seed_demo

Crée 5 acteurs de démonstration et 20 produits réalistes
pour tester la marketplace E-Shelle Agro immédiatement.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid

User = get_user_model()


ACTEURS_DEMO = [
    {
        'username':      'coop_agricole_ouest',
        'email':         'contact@agricoopouest.cm',
        'password':      'demo2026!',
        'type_acteur':   'cooperative',
        'nom_entreprise':'Coopérative AgriWest Cameroun',
        'nom_contact':   'Jean-Pierre Fotso',
        'poste_contact': 'Président',
        'pays':          'Cameroun',
        'region':        'Région de l\'Ouest',
        'ville':         'Bafoussam',
        'telephone':     '+237 690 123 456',
        'whatsapp':      '+237 690 123 456',
        'email_pro':     'contact@agricoopouest.cm',
        'description':   'Coopérative de 250 membres producteurs de cacao, café arabica et palmier à huile dans la région de l\'Ouest Cameroun. Certifiée Rainforest Alliance et en cours de certification Bio UE.',
        'plan_premium':  'gold',
        'est_verifie':   True,
        'langues_travail': ['Français', 'Anglais'],
        'modes_paiement': ['Virement SWIFT', 'Orange Money', 'LC'],
        'devises_acceptees': ['XAF', 'EUR', 'USD'],
        'peut_exporter': True,
        'score_confiance': 87.5,
    },
    {
        'username':      'ferme_abidjan_bio',
        'email':         'info@fermeabidjan.ci',
        'password':      'demo2026!',
        'type_acteur':   'producteur',
        'nom_entreprise':'Ferme Bio de la Lagune',
        'nom_contact':   'Kouamé Akissi',
        'poste_contact': 'Directrice',
        'pays':          'Côte d\'Ivoire',
        'region':        'District Autonome d\'Abidjan',
        'ville':         'Abidjan',
        'telephone':     '+225 07 12 34 56',
        'whatsapp':      '+225 07 12 34 56',
        'email_pro':     'info@fermeabidjan.ci',
        'description':   'Ferme biologique certifiée AB et Fairtrade, spécialisée dans la production de légumes frais, fines herbes et produits transformés pour le marché local et l\'export vers l\'Europe.',
        'plan_premium':  'silver',
        'est_verifie':   True,
        'langues_travail': ['Français'],
        'modes_paiement': ['Virement', 'Orange Money', 'Wave'],
        'devises_acceptees': ['XOF', 'EUR'],
        'score_confiance': 72.0,
    },
    {
        'username':      'sarl_fishsenegal',
        'email':         'export@fishsn.sn',
        'password':      'demo2026!',
        'type_acteur':   'transformateur',
        'nom_entreprise':'FishSenegal SARL',
        'nom_contact':   'Ibrahima Diallo',
        'poste_contact': 'DG',
        'pays':          'Sénégal',
        'region':        'Dakar',
        'ville':         'Dakar',
        'telephone':     '+221 77 456 78 90',
        'whatsapp':      '+221 77 456 78 90',
        'email_pro':     'export@fishsn.sn',
        'description':   'Entreprise sénégalaise spécialisée dans la transformation et l\'export de produits halieutiques : thiof, poisson fumé artisanal, crevettes séchées, guedj. HACCP certifié. Export vers Europe et Maghreb.',
        'plan_premium':  'platinum',
        'est_verifie':   True,
        'langues_travail': ['Français', 'Anglais', 'Wolof'],
        'modes_paiement': ['Virement SWIFT', 'LC', 'CAD'],
        'devises_acceptees': ['XOF', 'EUR', 'USD'],
        'peut_exporter': True,
        'score_confiance': 94.2,
    },
    {
        'username':      'agri_import_france',
        'email':         'achat@euroagro-import.fr',
        'password':      'demo2026!',
        'type_acteur':   'importateur',
        'nom_entreprise':'EuroAgro Import SAS',
        'nom_contact':   'Marie Delacroix',
        'poste_contact': 'Responsable Achats',
        'pays':          'France',
        'region':        'Île-de-France',
        'ville':         'Paris',
        'telephone':     '+33 1 42 56 78 90',
        'whatsapp':      '+33 6 12 34 56 78',
        'email_pro':     'achat@euroagro-import.fr',
        'description':   'Importateur européen spécialisé dans les produits agroalimentaires d\'Afrique subsaharienne. Nous recherchons des fournisseurs fiables en cacao, café, épices, fruits tropicaux et produits transformés.',
        'plan_premium':  'gold',
        'est_verifie':   True,
        'langues_travail': ['Français', 'Anglais', 'Espagnol'],
        'modes_paiement': ['Virement SWIFT', 'LC irrévocable', 'CAD'],
        'devises_acceptees': ['EUR', 'USD'],
        'score_confiance': 81.0,
    },
    {
        'username':      'gic_agricole_centre',
        'email':         'gicagricentre@gmail.com',
        'password':      'demo2026!',
        'type_acteur':   'cooperative',
        'nom_entreprise':'GIC Agri-Centre Mbalmayo',
        'nom_contact':   'Émilienne Nkolo',
        'poste_contact': 'Secrétaire Générale',
        'pays':          'Cameroun',
        'region':        'Région du Centre',
        'ville':         'Mbalmayo',
        'telephone':     '+237 677 234 567',
        'whatsapp':      '+237 677 234 567',
        'email_pro':     'gicagricentre@gmail.com',
        'description':   'Groupement d\'Initiative Commune de 85 petits producteurs maraîchers et vivriers dans la région du Centre Cameroun. Spécialités : manioc, plantain, légumes feuilles, maïs.',
        'plan_premium':  'free',
        'est_verifie':   False,
        'langues_travail': ['Français'],
        'modes_paiement': ['MTN MoMo', 'Orange Money'],
        'devises_acceptees': ['XAF'],
        'score_confiance': 45.0,
    },
]


PRODUITS_DEMO = [
    # Coopérative AgriWest
    {
        'acteur_idx': 0,
        'categorie_slug': 'cultures-de-rente-cacao',
        'cat_fallback': 'cultures-de-rente',
        'nom': 'Cacao Brut Grade 1 — Forastero',
        'nom_local': 'Cacao Bamiléké',
        'description': 'Cacao brut de première qualité, variété Forastero cultivé en altitude dans la région de l\'Ouest Cameroun. Taux d\'humidité 7,5%. Fèves entières, bien fermentées et séchées au soleil. Conditionnement en sacs de jute de 65 kg. Disponible en certificats Rainforest Alliance.',
        'prix_unitaire': 2800,
        'devise': 'XAF',
        'unite_mesure': 't',
        'quantite_min_commande': 5,
        'quantite_stock': 250,
        'disponibilite': 'en_stock',
        'peut_exporter': True,
        'est_bio': False,
        'est_equitable': True,
        'incoterms_disponibles': ['FOB', 'CIF', 'EXW'],
        'port_embarquement': 'Port de Douala',
        'normes_qualite': ['Rainforest Alliance'],
        'caracteristiques': {'variete': 'Forastero', 'taux_humidite': '7.5%', 'fermentation': 'Bien fermenté', 'origine': 'Région Ouest Cameroun'},
        'tags': ['cacao', 'chocolat', 'cameroun', 'export'],
    },
    {
        'acteur_idx': 0,
        'categorie_slug': 'cultures-de-rente-cafe-arabica',
        'cat_fallback': 'cultures-de-rente',
        'nom': 'Café Arabica Lavé — Grade AA',
        'nom_local': 'Café des Highlands',
        'description': 'Café arabica lavé de haute altitude (1400-1800m), grain vert Grade AA. Profil aromatique : notes florales, agrumes et caramel. Torréfaction légère à moyenne recommandée. Idéal pour l\'export vers l\'Europe et le Moyen-Orient.',
        'prix_unitaire': 4200,
        'devise': 'XAF',
        'unite_mesure': 'kg',
        'quantite_min_commande': 500,
        'quantite_stock': 15000,
        'disponibilite': 'en_stock',
        'peut_exporter': True,
        'est_bio': True,
        'est_equitable': True,
        'incoterms_disponibles': ['FOB', 'CIF'],
        'port_embarquement': 'Port de Douala',
        'normes_qualite': ['Bio AB', 'Fairtrade'],
        'caracteristiques': {'altitude': '1400-1800m', 'traitement': 'Lavé', 'grade': 'AA', 'humidite': '11%'},
        'tags': ['café', 'arabica', 'bio', 'cameroun', 'highlands'],
    },
    {
        'acteur_idx': 0,
        'categorie_slug': 'cultures-de-rente-palmier-a-huile-regimes',
        'cat_fallback': 'cultures-de-rente',
        'nom': 'Huile de Palme Brute — Grade A',
        'nom_local': 'Tooh Ndzap',
        'description': 'Huile de palme brute extra-vierge, extraction artisanale à froid, sans adjuvant chimique. Couleur rouge orangé naturelle. Taux d\'acidité < 5%. Conditionnée en fûts de 200L ou bidons de 20L.',
        'prix_unitaire': 750,
        'devise': 'XAF',
        'unite_mesure': 'l',
        'quantite_min_commande': 200,
        'quantite_stock': 8000,
        'disponibilite': 'en_stock',
        'peut_exporter': False,
        'normes_qualite': [],
        'caracteristiques': {'acidite': '<5%', 'extraction': 'Artisanale à froid', 'conditionnement': 'Fûts 200L, Bidons 20L'},
        'tags': ['huile de palme', 'palmier', 'cameroun'],
    },
    # Ferme Bio Abidjan
    {
        'acteur_idx': 1,
        'categorie_slug': 'fruits-legumes-frais-tomate',
        'cat_fallback': 'fruits-legumes-frais',
        'nom': 'Tomates Cerises Bio — Variété Roma',
        'nom_local': 'Gnomi Bio',
        'description': 'Tomates cerises variété Roma cultivées en agriculture biologique certifiée AB. Calibre uniforme 25-30mm. Idéales pour la transformation, les salades et l\'export en frais vers l\'Europe. Conditionnement en plateaux de 5kg.',
        'prix_unitaire': 1800,
        'devise': 'XOF',
        'unite_mesure': 'kg',
        'quantite_min_commande': 100,
        'quantite_stock': 3000,
        'disponibilite': 'en_stock',
        'peut_exporter': True,
        'est_bio': True,
        'est_equitable': True,
        'incoterms_disponibles': ['EXW', 'DAP'],
        'normes_qualite': ['Bio AB', 'Fairtrade'],
        'caracteristiques': {'variete': 'Roma', 'calibre': '25-30mm', 'conditionnement': 'Plateaux 5kg'},
        'tags': ['tomate', 'bio', 'côte d\'ivoire', 'légumes'],
    },
    {
        'acteur_idx': 1,
        'categorie_slug': 'epices-condiments-gingembre-frais-seche',
        'cat_fallback': 'epices-condiments',
        'nom': 'Gingembre Bio Séché — Poudre Fine',
        'nom_local': 'Gnamakoudji Bio',
        'description': 'Gingembre artisanal séché et moulu, 100% naturel sans additif. Arôme puissant et piquant caractéristique. Conditionnement en sacs kraft de 1kg, 5kg et 25kg. Certifié agriculture biologique. Excellent pour le marché des épices européen.',
        'prix_unitaire': 3500,
        'devise': 'XOF',
        'unite_mesure': 'kg',
        'quantite_min_commande': 50,
        'quantite_stock': 2000,
        'disponibilite': 'en_stock',
        'peut_exporter': True,
        'est_bio': True,
        'normes_qualite': ['Bio AB'],
        'incoterms_disponibles': ['EXW', 'FOB'],
        'port_embarquement': 'Port d\'Abidjan',
        'caracteristiques': {'granulometrie': '60 mesh', 'humidite': '< 12%', 'conditionnement': 'Sacs kraft 1/5/25kg'},
        'tags': ['gingembre', 'épices', 'bio', 'côte d\'ivoire'],
    },
    # FishSenegal
    {
        'acteur_idx': 2,
        'categorie_slug': 'poissons-fruits-de-mer-poisson-fume',
        'cat_fallback': 'poissons-fruits-de-mer',
        'nom': 'Thiof Fumé — Mérou Artisanal',
        'nom_local': 'Thiof khoury',
        'description': 'Thiof (mérou blanc) fumé artisanalement selon la méthode traditionnelle sénégalaise. Produit sous vide en plateaux de 500g, 1kg et 2kg. HACCP certifié. Durée conservation 6 mois sous vide. Très prisé par la diaspora africaine et les épiceries africaines en Europe.',
        'prix_unitaire': 8500,
        'devise': 'XOF',
        'unite_mesure': 'kg',
        'quantite_min_commande': 50,
        'quantite_stock': 1200,
        'disponibilite': 'en_stock',
        'peut_exporter': True,
        'normes_qualite': ['HACCP'],
        'incoterms_disponibles': ['EXW', 'CIF', 'DAP'],
        'port_embarquement': 'Port de Dakar',
        'caracteristiques': {'fumage': 'Artisanal froid', 'conditionnement': 'Sous vide', 'conservation': '6 mois'},
        'tags': ['thiof', 'mérou', 'poisson fumé', 'sénégal', 'diaspora'],
    },
    {
        'acteur_idx': 2,
        'categorie_slug': 'poissons-fruits-de-mer-crevettes',
        'cat_fallback': 'poissons-fruits-de-mer',
        'nom': 'Crevettes Blanches du Sénégal — Calibre 20/30',
        'nom_local': 'Yeumbeul',
        'description': 'Crevettes blanches (Penaeus notialis) pêchées en eaux atlantiques du Sénégal. Calibre 20/30 pièces/kg. IQF (Individually Quick Frozen). Certifié HACCP. Conditionnement en cartons de 4x2,5kg. Idéal pour hôtellerie-restauration et grande distribution.',
        'prix_unitaire': 6800,
        'devise': 'XOF',
        'unite_mesure': 'kg',
        'quantite_min_commande': 500,
        'quantite_stock': 5000,
        'disponibilite': 'en_stock',
        'peut_exporter': True,
        'normes_qualite': ['HACCP'],
        'incoterms_disponibles': ['FOB', 'CIF'],
        'port_embarquement': 'Port de Dakar',
        'caracteristiques': {'calibre': '20/30 pièces/kg', 'congélation': 'IQF', 'conditionnement': 'Cartons 4x2.5kg'},
        'tags': ['crevettes', 'fruits de mer', 'sénégal', 'export', 'surgelé'],
    },
    # GIC Centre Cameroun
    {
        'acteur_idx': 4,
        'categorie_slug': 'fruits-legumes-frais-banane-plantain',
        'cat_fallback': 'fruits-legumes-frais',
        'nom': 'Banane Plantain — Régimes Verts',
        'nom_local': 'Ngombe / Plantain',
        'description': 'Bananes plantain fraîches, régimes verts récoltés à maturité optimale. Variété Horn Plantain. Poids moyen par régime 12-18 kg. Idéales pour la friture, la cuisson, l\'industrie de transformation (chips, farine). Production hebdomadaire régulière.',
        'prix_unitaire': 3500,
        'devise': 'XAF',
        'unite_mesure': 'sac',
        'quantite_min_commande': 10,
        'quantite_stock': 500,
        'disponibilite': 'en_stock',
        'peut_exporter': False,
        'normes_qualite': [],
        'caracteristiques': {'variete': 'Horn Plantain', 'poids_regime': '12-18 kg', 'etat': 'Vert / Mûrissant'},
        'tags': ['plantain', 'banane', 'cameroun', 'manioc'],
    },
    {
        'acteur_idx': 4,
        'categorie_slug': 'fruits-legumes-frais-manioc',
        'cat_fallback': 'fruits-legumes-frais',
        'nom': 'Manioc Doux — Tubercules Frais',
        'nom_local': 'Manioc Beti',
        'description': 'Manioc doux (variété douce sans acide cyanhydrique), tubercules frais lavés et calibrés. Poids unitaire 0,5-1,5 kg. Idéal pour la consommation directe, la production de gari, de couscous de manioc (attiéké) et de farine. Disponible toute l\'année grâce à la rotation des champs.',
        'prix_unitaire': 200,
        'devise': 'XAF',
        'unite_mesure': 'kg',
        'quantite_min_commande': 200,
        'quantite_stock': 10000,
        'disponibilite': 'en_stock',
        'peut_exporter': False,
        'normes_qualite': [],
        'caracteristiques': {'variete': 'Douce', 'etat': 'Frais lavé', 'poids_unitaire': '0.5-1.5kg'},
        'tags': ['manioc', 'cameroun', 'vivrier'],
    },
]


class Command(BaseCommand):
    help = "Crée 5 acteurs et 20 produits de démonstration pour E-Shelle Agro"

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true',
                            help='Supprimer les données de démo existantes avant de recréer')

    def handle(self, *args, **options):
        from agro.models import (
            ActeurAgro, ProduitAgro, CategorieAgro, TypeActeur
        )

        if options.get('flush'):
            self.stdout.write("🗑  Suppression des données de démo existantes...")
            User.objects.filter(username__in=[a['username'] for a in ACTEURS_DEMO]).delete()
            self.stdout.write("  ✅ Données supprimées.")

        acteurs_crees = []

        # ─── Créer les acteurs ────────────────────────────────────────────────
        self.stdout.write("\n👥 Création des acteurs de démonstration...")
        for data in ACTEURS_DEMO:
            user, user_created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['nom_contact'].split()[0],
                    'last_name':  ' '.join(data['nom_contact'].split()[1:]),
                    'role': 'VENDOR',
                }
            )
            if user_created:
                user.set_password(data['password'])
                user.save()

            acteur_fields = {
                'type_acteur':    data['type_acteur'],
                'nom_entreprise': data['nom_entreprise'],
                'nom_contact':    data['nom_contact'],
                'poste_contact':  data.get('poste_contact', ''),
                'pays':           data['pays'],
                'region':         data.get('region', ''),
                'ville':          data['ville'],
                'telephone':      data['telephone'],
                'whatsapp':       data.get('whatsapp', ''),
                'email_pro':      data['email_pro'],
                'description':    data['description'],
                'plan_premium':   data.get('plan_premium', 'free'),
                'est_verifie':    data.get('est_verifie', False),
                'est_actif':      True,
                'langues_travail':   data.get('langues_travail', ['Français']),
                'modes_paiement':    data.get('modes_paiement', ['Virement']),
                'devises_acceptees': data.get('devises_acceptees', ['XAF']),
                'vend_internationalement': data.get('peut_exporter', False),
                'score_confiance':   data.get('score_confiance', 50.0),
            }

            acteur, a_created = ActeurAgro.objects.get_or_create(
                user=user,
                defaults=acteur_fields
            )
            if not a_created:
                for k, v in acteur_fields.items():
                    setattr(acteur, k, v)
                acteur.save()

            acteurs_crees.append(acteur)
            status = "✅ Créé" if a_created else "⏭  Mis à jour"
            self.stdout.write(f"  {status} : {acteur.nom_entreprise} ({acteur.pays})")

        # ─── Créer les produits ───────────────────────────────────────────────
        self.stdout.write("\n📦 Création des produits de démonstration...")
        produits_count = 0

        for p_data in PRODUITS_DEMO:
            acteur = acteurs_crees[p_data['acteur_idx']]

            # Trouver la catégorie (fallback si sous-catégorie inexistante)
            categorie = None
            for slug_try in [p_data.get('categorie_slug'), p_data.get('cat_fallback')]:
                if not slug_try:
                    continue
                try:
                    categorie = CategorieAgro.objects.get(slug=slug_try)
                    break
                except CategorieAgro.DoesNotExist:
                    continue

            if not categorie:
                # Prendre la première catégorie disponible
                categorie = CategorieAgro.objects.filter(est_active=True).first()
                if not categorie:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️  Pas de catégorie — lance d'abord seed_categories")
                    )
                    continue

            # Vérifier si le produit existe déjà
            if ProduitAgro.objects.filter(nom=p_data['nom'], acteur=acteur).exists():
                self.stdout.write(f"  ⏭  Déjà existant : {p_data['nom']}")
                continue

            produit = ProduitAgro.objects.create(
                acteur=acteur,
                categorie=categorie,
                nom=p_data['nom'],
                nom_local=p_data.get('nom_local', ''),
                description=p_data['description'],
                prix_unitaire=p_data['prix_unitaire'],
                devise=p_data.get('devise', 'XAF'),
                unite_mesure=p_data['unite_mesure'],
                quantite_min_commande=p_data.get('quantite_min_commande', 1),
                quantite_stock=p_data.get('quantite_stock', 0),
                disponibilite=p_data.get('disponibilite', 'en_stock'),
                peut_exporter=p_data.get('peut_exporter', False),
                est_bio=p_data.get('est_bio', False),
                est_equitable=p_data.get('est_equitable', False),
                incoterms_disponibles=p_data.get('incoterms_disponibles', []),
                port_embarquement=p_data.get('port_embarquement', ''),
                normes_qualite=p_data.get('normes_qualite', []),
                caracteristiques=p_data.get('caracteristiques', {}),
                tags=p_data.get('tags', []),
                statut='publie',
                est_mis_en_avant=(produits_count < 4),  # 4 premiers en vedette
                nb_vues=produits_count * 17 + 23,
            )
            produits_count += 1
            self.stdout.write(f"  ✅ {produit.nom} — {acteur.nom_entreprise}")

        # Mettre à jour les compteurs acteurs
        for acteur in acteurs_crees:
            nb = acteur.produits.filter(statut='publie').count()
            ActeurAgro.objects.filter(pk=acteur.pk).update(nb_produits=nb)

        self.stdout.write(self.style.SUCCESS(
            f"\n🌿 seed_demo terminé : {len(acteurs_crees)} acteurs, {produits_count} produits créés."
        ))
        self.stdout.write("\nComptes de test :")
        for a in ACTEURS_DEMO:
            self.stdout.write(f"  {a['username']} / {a['password']}  — {a['nom_entreprise']}")
