"""
Usage: python manage.py setup_classes
Crée toutes les classes du programme MINESEC avec leurs chapitres.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from math_cm.models import Classe, Chapitre

PROGRAMME = [
    {
        'nom': '3eme', 'label': 'Troisième', 'examen': 'bepc', 'ordre': 1,
        'couleur': '#2196F3',
        'chapitres': [
            ('Ensembles et applications', 'logique'),
            ('Nombres relatifs et calcul littéral', 'algebre'),
            ('Équations et inéquations du premier degré', 'algebre'),
            ('Systèmes d\'équations', 'algebre'),
            ('Fonctions numériques — généralités', 'analyse'),
            ('Fonction linéaire et affine', 'analyse'),
            ('Proportionnalité et pourcentages', 'arithmetique'),
            ('Statistiques descriptives', 'statistiques'),
            ('Triangles — propriétés et calculs', 'geometrie'),
            ('Théorème de Pythagore', 'geometrie'),
            ('Théorème de Thalès', 'geometrie'),
            ('Trigonométrie dans le triangle rectangle', 'trigonometrie'),
            ('Cercles et angles inscrits', 'geometrie'),
            ('Aires et volumes', 'geometrie'),
            ('Puissances et notation scientifique', 'arithmetique'),
        ]
    },
    {
        'nom': '2nde', 'label': 'Seconde', 'examen': '', 'ordre': 2,
        'couleur': '#9C27B0',
        'chapitres': [
            ('Logique et raisonnement mathématique', 'logique'),
            ('Ensembles de nombres — ℕ, ℤ, ℚ, ℝ', 'logique'),
            ('Calcul algébrique et identités remarquables', 'algebre'),
            ('Équations et inéquations du 2nd degré', 'algebre'),
            ('Systèmes d\'équations et de Cramer', 'algebre'),
            ('Fonctions — Généralités et représentations', 'analyse'),
            ('Fonction du 2nd degré — Parabole', 'analyse'),
            ('Fonctions de référence (√x, 1/x, |x|)', 'analyse'),
            ('Géométrie plane — Vecteurs', 'geometrie'),
            ('Droites et équations de droites', 'geometrie'),
            ('Cercle et équation du cercle', 'geometrie'),
            ('Trigonométrie — Cercle trigonométrique', 'trigonometrie'),
            ('Statistiques et représentations graphiques', 'statistiques'),
            ('Probabilités — Introduction', 'statistiques'),
            ('Suites numériques — Introduction', 'suites'),
            ('Arithmétique — PGCD, PPCM, divisibilité', 'arithmetique'),
        ]
    },
    {
        'nom': '1ere_c', 'label': 'Première C', 'examen': 'probatoire', 'ordre': 3,
        'couleur': '#FF5722',
        'chapitres': [
            ('Suites arithmétiques et géométriques', 'suites'),
            ('Limites de suites', 'suites'),
            ('Limites de fonctions', 'analyse'),
            ('Continuité des fonctions', 'analyse'),
            ('Dérivabilité — Définition et calcul', 'analyse'),
            ('Tableau de variations et extrema', 'analyse'),
            ('Étude complète d\'une fonction', 'analyse'),
            ('Fonction exponentielle (eˣ)', 'analyse'),
            ('Fonction logarithme népérien', 'analyse'),
            ('Trigonométrie — Formules et équations', 'trigonometrie'),
            ('Géométrie dans l\'espace — Plans et droites', 'geometrie'),
            ('Vecteurs dans l\'espace', 'geometrie'),
            ('Géométrie analytique dans le plan', 'geometrie'),
            ('Probabilités — Dénombrement', 'statistiques'),
            ('Statistiques — Moyenne, variance, écart-type', 'statistiques'),
            ('Arithmétique — Nombres premiers, congruences', 'arithmetique'),
            ('Polynômes et factorisation', 'algebre'),
            ('Nombres complexes — Introduction', 'complexes'),
        ]
    },
    {
        'nom': '1ere_d', 'label': 'Première D', 'examen': 'probatoire', 'ordre': 4,
        'couleur': '#FF5722',
        'chapitres': [
            ('Suites arithmétiques et géométriques', 'suites'),
            ('Limites et continuité', 'analyse'),
            ('Dérivées et applications', 'analyse'),
            ('Fonctions exponentielle et logarithme', 'analyse'),
            ('Trigonométrie avancée', 'trigonometrie'),
            ('Géométrie dans l\'espace', 'geometrie'),
            ('Probabilités et dénombrement', 'statistiques'),
            ('Statistiques — Paramètres de dispersion', 'statistiques'),
            ('Polynômes', 'algebre'),
            ('Nombres complexes — Introduction', 'complexes'),
            ('Arithmétique', 'arithmetique'),
            ('Géométrie analytique', 'geometrie'),
        ]
    },
    {
        'nom': '1ere_a', 'label': 'Première A', 'examen': 'probatoire', 'ordre': 5,
        'couleur': '#607D8B',
        'chapitres': [
            ('Suites numériques', 'suites'),
            ('Fonctions — Limites et continuité', 'analyse'),
            ('Dérivées et applications', 'analyse'),
            ('Statistiques descriptives avancées', 'statistiques'),
            ('Probabilités et dénombrement', 'statistiques'),
            ('Géométrie plane — Transformations', 'geometrie'),
            ('Trigonométrie appliquée', 'trigonometrie'),
            ('Systèmes d\'équations avancés', 'algebre'),
            ('Économie mathématique — Fonctions coût/recette', 'analyse'),
            ('Arithmétique financière', 'arithmetique'),
        ]
    },
    {
        'nom': 'tle_c', 'label': 'Terminale C', 'examen': 'baccalaureat', 'ordre': 6,
        'couleur': '#F44336',
        'chapitres': [
            ('Primitives et calcul intégral', 'analyse'),
            ('Équations différentielles', 'analyse'),
            ('Nombres complexes — Forme trigonométrique', 'complexes'),
            ('Nombres complexes — Applications géométriques', 'complexes'),
            ('Suites — Convergence et divergence', 'suites'),
            ('Fonctions logarithme et exponentielle avancées', 'analyse'),
            ('Développements limités', 'analyse'),
            ('Géométrie dans l\'espace — Plans et sphères', 'geometrie'),
            ('Matrices et systèmes linéaires', 'matrices'),
            ('Déterminants et applications', 'matrices'),
            ('Probabilités — Variables aléatoires discrètes', 'statistiques'),
            ('Loi binomiale et loi de Poisson', 'statistiques'),
            ('Trigonométrie — Transformations et équations', 'trigonometrie'),
            ('Arithmétique — Théorie des nombres', 'arithmetique'),
            ('Courbes paramétriques et polaires', 'analyse'),
            ('Loi normale et statistiques inférentielles', 'statistiques'),
        ]
    },
    {
        'nom': 'tle_d', 'label': 'Terminale D', 'examen': 'baccalaureat', 'ordre': 7,
        'couleur': '#F44336',
        'chapitres': [
            ('Primitives et intégration', 'analyse'),
            ('Équations différentielles', 'analyse'),
            ('Nombres complexes', 'complexes'),
            ('Suites numériques — Convergence', 'suites'),
            ('Fonctions logarithme et exponentielle', 'analyse'),
            ('Géométrie dans l\'espace', 'geometrie'),
            ('Matrices', 'matrices'),
            ('Probabilités — Variables aléatoires', 'statistiques'),
            ('Loi binomiale', 'statistiques'),
            ('Trigonométrie', 'trigonometrie'),
            ('Arithmétique', 'arithmetique'),
        ]
    },
    {
        'nom': 'tle_a', 'label': 'Terminale A', 'examen': 'baccalaureat', 'ordre': 8,
        'couleur': '#795548',
        'chapitres': [
            ('Fonctions et dérivées — Révisions approfondies', 'analyse'),
            ('Calcul intégral — Applications économiques', 'analyse'),
            ('Probabilités et statistiques', 'statistiques'),
            ('Mathématiques financières', 'arithmetique'),
            ('Programmation linéaire', 'algebre'),
            ('Géométrie analytique', 'geometrie'),
            ('Logique mathématique et démonstration', 'logique'),
            ('Suites et applications économiques', 'suites'),
        ]
    },
]


class Command(BaseCommand):
    help = 'Crée toutes les classes et chapitres du programme MINESEC'

    def handle(self, *args, **options):
        total_classes = 0
        total_chapitres = 0

        for prog in PROGRAMME:
            classe, created = Classe.objects.update_or_create(
                nom=prog['nom'],
                defaults={
                    'label': prog['label'],
                    'examen_fin_annee': prog['examen'],
                    'couleur': prog['couleur'],
                    'ordre': prog['ordre'],
                    'is_active': True,
                }
            )
            if created:
                total_classes += 1
                self.stdout.write(f"  ✅ Classe créée : {classe.label}")

            for i, (titre, categorie) in enumerate(prog['chapitres'], start=1):
                slug = slugify(f"{prog['nom']}-{i}-{titre}")[:210]
                _, ch_created = Chapitre.objects.update_or_create(
                    classe=classe, numero=i,
                    defaults={
                        'titre': titre,
                        'slug': slug,
                        'categorie': categorie,
                        'difficulte': 2,
                        'is_published': True,
                    }
                )
                if ch_created:
                    total_chapitres += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ {total_classes} classes et {total_chapitres} chapitres créés."
        ))
