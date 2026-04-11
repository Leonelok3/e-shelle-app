"""
python manage.py seed_categories

Crée les 12 catégories principales et leurs sous-catégories
pour la marketplace E-Shelle Agro.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify


CATEGORIES = [
    {
        'nom': 'Céréales & Légumineuses',
        'icone': '🌾',
        'description': 'Maïs, riz, sorgho, mil, soja, haricot, arachide, blé...',
        'ordre': 1,
        'sous': [
            'Maïs', 'Riz paddy', 'Sorgho', 'Mil / Millet', 'Blé',
            'Soja', 'Haricot', 'Arachide / Cacahuète', 'Niébé', 'Pois chiche',
        ],
    },
    {
        'nom': 'Fruits & Légumes Frais',
        'icone': '🥬',
        'description': 'Plantain, manioc, igname, tomate, gombo, piment, légumes feuilles...',
        'ordre': 2,
        'sous': [
            'Banane plantain', 'Manioc', 'Igname', 'Tomate', 'Gombo',
            'Piment', 'Aubergine africaine', 'Légumes feuilles', 'Patate douce', 'Taro',
        ],
    },
    {
        'nom': 'Cultures de Rente',
        'icone': '🍃',
        'description': 'Cacao, café, coton, hévéa, palmier à huile, anacarde, vanille...',
        'ordre': 3,
        'sous': [
            'Cacao', 'Café Arabica', 'Café Robusta', 'Palmier à huile (régimes)',
            'Anacarde / Noix de cajou', 'Coton', 'Hévéa (latex)', 'Vanille', 'Poivre', 'Gingembre',
        ],
    },
    {
        'nom': 'Viandes & Produits Animaux',
        'icone': '🥩',
        'description': 'Bœuf, porc, volaille, agneau, gibier, charcuterie africaine...',
        'ordre': 4,
        'sous': [
            'Bœuf', 'Porc', 'Volaille (poulet, pintade)', 'Agneau / Mouton',
            'Chèvre', 'Gibier', 'Charcuterie africaine', 'Abats',
        ],
    },
    {
        'nom': 'Poissons & Fruits de Mer',
        'icone': '🐟',
        'description': 'Tilapia, capitaine, crevettes, thon, poisson fumé, séché...',
        'ordre': 5,
        'sous': [
            'Tilapia frais', 'Capitaine / Poisson bar', 'Crevettes',
            'Thon', 'Sardines', 'Poisson fumé', 'Poisson séché / salé',
            'Crevettes séchées', 'Carpe', 'Silure',
        ],
    },
    {
        'nom': 'Produits Laitiers & Œufs',
        'icone': '🥛',
        'description': 'Lait frais, fromage, beurre de karité, yaourt, œufs...',
        'ordre': 6,
        'sous': [
            'Lait frais', 'Lait en poudre', 'Yaourt', 'Fromage artisanal',
            'Beurre clarifié', 'Beurre de karité alimentaire', 'Œufs de poule', 'Œufs de caille',
        ],
    },
    {
        'nom': 'Produits Transformés',
        'icone': '🫙',
        'description': 'Huile de palme, farine de manioc, attiéké, gari, ndolé en conserve...',
        'ordre': 7,
        'sous': [
            'Huile de palme', 'Huile de palmiste', "Farine de manioc / Gari / Attiéké",
            'Farine de maïs', 'Farine de soja', 'Concentré de tomate artisanal',
            'Pâte d\'arachide', 'Sucre de canne artisanal', 'Miel', 'Jus de fruits artisanaux',
        ],
    },
    {
        'nom': 'Épices & Condiments',
        'icone': '🌿',
        'description': 'Poivre, gingembre, curcuma, hibiscus, feuilles séchées, épices locales...',
        'ordre': 8,
        'sous': [
            'Poivre blanc / noir', 'Gingembre frais / séché', 'Curcuma',
            'Piment séché / moulu', 'Graines de djansang', 'Hibiscus (bissap)',
            'Neem / Moringa', 'Cannelle', 'Muscade', 'Feuilles séchées',
        ],
    },
    {
        'nom': 'Bois & Biomasse',
        'icone': '🪵',
        'description': 'Bois de chauffe, charbon végétal, coques de cacao, biomasse...',
        'ordre': 9,
        'sous': [
            'Charbon végétal', 'Bois de chauffe', 'Coques de cacao (biocombustible)',
            'Bagasse de canne', 'Balles de riz', 'Biomasse agricole',
        ],
    },
    {
        'nom': 'Intrants & Équipements',
        'icone': '🧴',
        'description': 'Semences, engrais, matériel agricole, irrigation, pesticides bio...',
        'ordre': 10,
        'sous': [
            'Semences certifiées', 'Semences améliorées', 'Engrais organiques',
            'Engrais minéraux', 'Phytosanitaires', 'Matériel irrigation',
            'Outils agricoles manuels', 'Équipements post-récolte',
        ],
    },
    {
        'nom': 'Animaux Vivants',
        'icone': '🐄',
        'description': 'Bovins, ovins, volailles sur pied, poissons d\'élevage, chèvres...',
        'ordre': 11,
        'sous': [
            'Bovins', 'Ovins', 'Caprins (chèvres)', 'Porcins',
            'Volailles (poulet chair / ponte)', 'Pintades', 'Lapins',
            'Alevins (poissons)', 'Escargots géants africains',
        ],
    },
    {
        'nom': 'Agriculture Bio & Équitable',
        'icone': '🌱',
        'description': 'Produits certifiés agriculture biologique et commerce équitable...',
        'ordre': 12,
        'sous': [
            'Cacao certifié bio', 'Café certifié Fairtrade',
            'Fruits & légumes bio', 'Épices bio certifiées',
            'Produits Rainforest Alliance', 'Miel bio',
        ],
    },
]


class Command(BaseCommand):
    help = "Crée les catégories et sous-catégories agroalimentaires initiales"

    def handle(self, *args, **options):
        from agro.models import CategorieAgro

        created_count  = 0
        existing_count = 0

        for cat_data in CATEGORIES:
            slug_parent = slugify(cat_data['nom'])
            parent, created = CategorieAgro.objects.get_or_create(
                slug=slug_parent,
                defaults={
                    'nom':         cat_data['nom'],
                    'icone':       cat_data['icone'],
                    'description': cat_data['description'],
                    'ordre':       cat_data['ordre'],
                    'est_active':  True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ {cat_data['icone']} {cat_data['nom']}")
            else:
                existing_count += 1
                self.stdout.write(f"  ⏭  {cat_data['nom']} (déjà existant)")

            # Sous-catégories
            for i, sous_nom in enumerate(cat_data.get('sous', []), 1):
                slug_sous = slugify(f"{slug_parent}-{sous_nom}")
                sous, s_created = CategorieAgro.objects.get_or_create(
                    slug=slug_sous,
                    defaults={
                        'nom':        sous_nom,
                        'parent':     parent,
                        'ordre':      i,
                        'est_active': True,
                    }
                )
                if s_created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n🌿 seed_categories terminé : {created_count} créées, {existing_count} déjà existantes."
        ))
