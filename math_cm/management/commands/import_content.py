"""
Importe du contenu JSON généré manuellement dans la base de données.

Usage:
  python manage.py import_content --file math_cm/fixtures/content/3eme/ch01_lecons.json
  python manage.py import_content --file math_cm/fixtures/content/3eme/ch01_exercices.json
  python manage.py import_content --file math_cm/fixtures/content/3eme/ch01_complet.json

Types acceptés dans le JSON :
  "lecons"       → importe uniquement les leçons
  "exercices"    → importe uniquement les exercices
  "cours_complet"→ importe leçons + exercices en une seule fois
  "epreuve"      → importe une épreuve type examen
"""
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from math_cm.models import Chapitre, Lecon, Exercice, EpreuveExamen, Classe


class Command(BaseCommand):
    help = 'Importe du contenu JSON dans la base de données MathCM'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Chemin vers le fichier JSON')

    def handle(self, *args, **options):
        filepath = options['file']
        if not os.path.exists(filepath):
            self.stdout.write(self.style.ERROR(f"Fichier introuvable : {filepath}"))
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        content_type = data.get('type')
        chapitre_slug = data.get('chapitre_slug')

        # ── COURS COMPLET (leçons + exercices ensemble) ───────────────
        if content_type == 'cours_complet':
            try:
                chapitre = Chapitre.objects.get(slug=chapitre_slug)
            except Chapitre.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Chapitre '{chapitre_slug}' introuvable"))
                return

            self.stdout.write(f"\n📚 Import cours complet : {chapitre.titre}")

            # Leçons
            lecons_data = data.get('lecons', [])
            lecons_crees = 0
            for ld in lecons_data:
                base_slug = slugify(f"{chapitre.slug}-l{ld['ordre']}-{ld['titre']}")[:210]
                slug = base_slug
                i = 1
                while Lecon.objects.filter(slug=slug).exclude(chapitre=chapitre, ordre=ld['ordre']).exists():
                    slug = f"{base_slug}-{i}"; i += 1
                _, was_created = Lecon.objects.update_or_create(
                    chapitre=chapitre, ordre=ld['ordre'],
                    defaults={
                        'titre': ld['titre'],
                        'slug': slug,
                        'type_lecon': ld.get('type_lecon', 'definition'),
                        'contenu': ld['contenu'],
                        'duree_lecture': ld.get('duree_lecture', 15),
                        'is_free': ld.get('is_free', False),
                        'is_published': True,
                    }
                )
                icon = '✅' if was_created else '🔄'
                self.stdout.write(f"  {icon} Leçon {ld['ordre']} : {ld['titre']}")
                if was_created:
                    lecons_crees += 1

            # Exercices
            exercices_data = data.get('exercices', [])
            exercices_crees = 0
            for ex in exercices_data:
                numero = ex.get('numero', chapitre.exercices.count() + 1)
                # Gérer options_qcm : peut être liste de listes (une par question) ou liste plate
                options = ex.get('options_qcm', [])
                if options and isinstance(options[0], list):
                    # Format liste de listes → on prend la première liste pour l'exercice global
                    options = options[0] if len(options) == 1 else options
                _, was_created = Exercice.objects.update_or_create(
                    chapitre=chapitre, numero=numero,
                    defaults={
                        'titre': ex['titre'],
                        'type_exercice': ex.get('type_exercice', 'application'),
                        'niveau': ex.get('niveau', 'entrainement'),
                        'enonce': ex['enonce'],
                        'correction': ex['correction'],
                        'options_qcm': options,
                        'bareme': ex.get('bareme', 5),
                        'duree_recommandee': ex.get('duree_recommandee', 20),
                        'is_published': True,
                    }
                )
                icon = '✅' if was_created else '🔄'
                self.stdout.write(f"  {icon} Ex.{numero} : {ex['titre']}")
                if was_created:
                    exercices_crees += 1

            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Import terminé : {lecons_crees} leçons + {exercices_crees} exercices créés"
            ))
            return

        # ── LEÇONS ────────────────────────────────────────────────────
        if content_type == 'lecons':
            try:
                chapitre = Chapitre.objects.get(slug=chapitre_slug)
            except Chapitre.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Chapitre '{chapitre_slug}' introuvable"))
                return

            created = 0
            for ld in data['lecons']:
                base_slug = slugify(f"{chapitre.slug}-l{ld['ordre']}-{ld['titre']}")[:210]
                slug = base_slug
                i = 1
                while Lecon.objects.filter(slug=slug).exclude(chapitre=chapitre, ordre=ld['ordre']).exists():
                    slug = f"{base_slug}-{i}"; i += 1

                _, was_created = Lecon.objects.update_or_create(
                    chapitre=chapitre, ordre=ld['ordre'],
                    defaults={
                        'titre': ld['titre'],
                        'slug': slug,
                        'type_lecon': ld.get('type_lecon', 'definition'),
                        'contenu': ld['contenu'],
                        'duree_lecture': ld.get('duree_lecture', 15),
                        'is_free': ld.get('is_free', False),
                        'is_published': True,
                    }
                )
                if was_created:
                    created += 1
                    self.stdout.write(f"  ✅ Leçon {ld['ordre']} : {ld['titre']}")
                else:
                    self.stdout.write(f"  🔄 Mise à jour : {ld['titre']}")

            self.stdout.write(self.style.SUCCESS(f"\n✅ {created} leçons importées pour '{chapitre.titre}'"))

        # ── EXERCICES ─────────────────────────────────────────────────
        elif content_type == 'exercices':
            try:
                chapitre = Chapitre.objects.get(slug=chapitre_slug)
            except Chapitre.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Chapitre '{chapitre_slug}' introuvable"))
                return

            offset = chapitre.exercices.count()
            created = 0
            for i, ex in enumerate(data['exercices']):
                numero = ex.get('numero', offset + i + 1)
                _, was_created = Exercice.objects.update_or_create(
                    chapitre=chapitre, numero=numero,
                    defaults={
                        'titre': ex['titre'],
                        'type_exercice': ex.get('type_exercice', 'qcm'),
                        'niveau': ex.get('niveau', 'entrainement'),
                        'enonce': ex['enonce'],
                        'correction': ex['correction'],
                        'options_qcm': ex.get('options_qcm', []),
                        'bareme': ex.get('bareme', 5),
                        'duree_recommandee': ex.get('duree_recommandee', 20),
                        'is_published': True,
                    }
                )
                if was_created:
                    created += 1
                    self.stdout.write(f"  ✅ Ex.{numero} : {ex['titre']}")

            self.stdout.write(self.style.SUCCESS(f"\n✅ {created} exercices importés pour '{chapitre.titre}'"))

        # ── ÉPREUVE EXAMEN ────────────────────────────────────────────
        elif content_type == 'epreuve':
            classe_nom = data.get('classe')
            try:
                classe = Classe.objects.get(nom=classe_nom)
            except Classe.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Classe '{classe_nom}' introuvable"))
                return

            ep = data['epreuve']
            slug = slugify(ep['titre'])[:48]
            obj, created = EpreuveExamen.objects.update_or_create(
                slug=slug,
                defaults={
                    'titre': ep['titre'],
                    'classe': classe,
                    'type_examen': ep.get('type_examen', 'entrainement'),
                    'serie': ep.get('serie', 'toutes'),
                    'annee': ep.get('annee'),
                    'region': ep.get('region', ''),
                    'duree': ep.get('duree', 180),
                    'bareme_total': ep.get('bareme_total', 20),
                    'contenu': ep.get('contenu', {}),
                    'correction_complete': ep.get('correction_complete', {}),
                    'is_premium': ep.get('is_premium', False),
                    'is_published': True,
                }
            )
            action = "créée" if created else "mise à jour"
            self.stdout.write(self.style.SUCCESS(f"✅ Épreuve {action} : {ep['titre']}"))

        else:
            self.stdout.write(self.style.ERROR(
                f"Type '{content_type}' inconnu. Valeurs acceptées : cours_complet, lecons, exercices, epreuve"
            ))
