"""
import_french_lessons.py — Importe les leçons françaises (CE/EE/EO)
depuis les fichiers data/lessons_json/ vers preparation_tests.

Format JSON attendu (tous les fichiers fr) :
{
  "skill": "ce" | "ee" | "eo",
  "level": "A1" | "A2" | "B1" | "B2" | "C1" | "C2",
  "lessons": [
    # CE (Compréhension Écrite) :
    {
      "title": "...",
      "reading_text": "<p>...</p>",
      "questions": [
        {"question_text": "...", "option_a": "...", "option_b": "...",
         "option_c": "...", "option_d": "...", "correct_option": "C", "summary": "..."}
      ]
    },
    # EE (Expression Écrite) :
    {
      "topic": "...",
      "instructions": "...",
      "min_words": 40,
      "sample_answer": "..."
    },
    # EO (Expression Orale) :
    {
      "topic": "...",
      "instructions": "...",
      "expected_points": ["...", "..."]
    }
  ]
}

Usage :
    python manage.py import_french_lessons --file data/lessons_json/ce_A1.json
    python manage.py import_french_lessons --all          # tous les fichiers fr
    python manage.py import_french_lessons --all --flush  # repart de zero
"""
import json
import os
import glob
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from preparation_tests.models import CourseLesson, CourseExercise

VALID_SKILLS = {"ce", "ee", "eo", "co"}
VALID_LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "lessons_json"


def _make_slug(section, level, title, idx):
    base = slugify(f"{section}-{level}-{title}")[:46]
    # Ensure uniqueness by appending index if slug already used
    slug = base
    counter = 1
    while CourseLesson.objects.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def _build_ce_content(lesson):
    """CE : texte de lecture + chapeau intro."""
    title = lesson.get("title", "")
    reading = lesson.get("reading_text", "")
    return f"<h2>{title}</h2>\n{reading}"


def _build_ee_content(lesson):
    """EE : sujet + consigne + exemple de réponse."""
    topic = lesson.get("topic", "")
    instructions = lesson.get("instructions", "")
    min_words = lesson.get("min_words", "")
    sample = lesson.get("sample_answer", "")
    html = f"<h2>{topic}</h2>\n"
    if instructions:
        html += f"<div class='ee-instructions'><strong>Consigne :</strong> {instructions}</div>\n"
    if min_words:
        html += f"<p class='ee-minwords'>Nombre de mots minimum : <strong>{min_words}</strong></p>\n"
    if sample:
        safe_sample = sample.replace("\n", "<br>")
        html += f"<details class='ee-sample'><summary>Voir un exemple de réponse</summary><p>{safe_sample}</p></details>\n"
    return html


def _build_eo_content(lesson):
    """EO : sujet + consigne + points attendus."""
    topic = lesson.get("topic", "")
    instructions = lesson.get("instructions", "")
    points = lesson.get("expected_points", [])
    html = f"<h2>{topic}</h2>\n"
    if instructions:
        html += f"<div class='eo-instructions'><strong>Consigne :</strong> {instructions}</div>\n"
    if points:
        html += "<ul class='eo-points'>\n"
        for p in (points if isinstance(points, list) else [points]):
            html += f"  <li>{p}</li>\n"
        html += "</ul>\n"
    return html


def _import_file(filepath, stdout, style, flush=False):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    # Format 1 : dict avec metadata {"skill":..., "level":..., "lessons":[...]}
    # Format 2 : liste directe [{"title":..., "reading_text":..., "questions":[...]}]
    if isinstance(data, list):
        # Déduire skill et level depuis le nom du fichier (ex: ce_A2_new26.json)
        fname = os.path.basename(filepath)
        parts = fname.split("_")
        skill = parts[0].lower()   # ce, ee, eo
        level = parts[1].upper()   # A1, A2...
        lessons = data
    elif isinstance(data, dict) and "lessons" in data:
        skill   = data.get("skill", "").lower()
        level   = data.get("level", "").upper()
        lessons = data.get("lessons", [])
    else:
        stdout.write(style.WARNING(f"  Fichier ignoré (format inattendu) : {filepath}"))
        return 0, 0

    if skill not in VALID_SKILLS:
        stdout.write(style.WARNING(f"  Skill inconnu '{skill}' — ignoré"))
        return 0, 0
    if level not in VALID_LEVELS:
        stdout.write(style.WARNING(f"  Level inconnu '{level}' — ignoré"))
        return 0, 0

    if flush:
        deleted = CourseLesson.objects.filter(section=skill, level=level).count()
        CourseLesson.objects.filter(section=skill, level=level).delete()
        stdout.write(style.WARNING(f"  {deleted} leçon(s) {skill.upper()}/{level} supprimée(s)"))

    lesson_count = 0
    exercise_count = 0

    for idx, lesson_data in enumerate(lessons):
        with transaction.atomic():
            # ── Titre ──────────────────────────────────────────────
            if skill == "ce":
                title = lesson_data.get("title", f"Leçon {idx+1}")
                content = _build_ce_content(lesson_data)
            else:
                title = lesson_data.get("topic", f"Sujet {idx+1}")
                if skill == "ee":
                    content = _build_ee_content(lesson_data)
                else:  # eo
                    content = _build_eo_content(lesson_data)

            title = title[:255]
            order = CourseLesson.objects.filter(section=skill, level=level).count() + 1

            slug = _make_slug(skill, level, title, idx)

            lesson_obj, created = CourseLesson.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "section": skill,
                    "level": level,
                    "content_html": content,
                    "locale": "fr",
                    "order": order,
                    "is_published": True,
                },
            )

            if not created:
                # Leçon déjà importée, on passe
                continue

            lesson_count += 1

            # ── Exercices QCM (CE uniquement) ──────────────────────
            if skill == "ce":
                questions = lesson_data.get("questions", [])
                for q_idx, q in enumerate(questions):
                    correct = q.get("correct_option", "A").upper()
                    if correct not in ("A", "B", "C", "D"):
                        correct = "A"
                    CourseExercise.objects.create(
                        lesson=lesson_obj,
                        title=f"Question {q_idx+1}",
                        instruction="",
                        question_text=q.get("question_text", ""),
                        option_a=q.get("option_a", "")[:255],
                        option_b=q.get("option_b", "")[:255],
                        option_c=q.get("option_c", "")[:255],
                        option_d=q.get("option_d", "")[:255],
                        correct_option=correct,
                        summary=q.get("summary", ""),
                        order=q_idx + 1,
                        is_active=True,
                    )
                    exercise_count += 1

    return lesson_count, exercise_count


class Command(BaseCommand):
    help = "Importe les leçons françaises CE/EE/EO depuis data/lessons_json/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file", type=str, default=None,
            help="Fichier JSON à importer (ex: data/lessons_json/ce_A1.json)",
        )
        parser.add_argument(
            "--all", action="store_true",
            help="Importer tous les fichiers ce_*.json, ee_*.json, eo_*.json",
        )
        parser.add_argument(
            "--flush", action="store_true",
            help="Supprimer les leçons existantes du même skill/level avant import",
        )

    def handle(self, *args, **options):
        flush = options["flush"]

        if options["all"]:
            patterns = ["ce_*.json", "ee_*.json", "eo_*.json"]
            files = []
            for pat in patterns:
                files += sorted(glob.glob(str(DATA_DIR / pat)))
            # Exclure les fichiers _new, _extra, _final, _part (déjà inclus dans _all)
            # On les garde tous pour avoir le maximum de contenu
        elif options["file"]:
            files = [options["file"]]
        else:
            self.stderr.write("Précise --file <chemin> ou --all")
            return

        total_lessons = 0
        total_exercises = 0

        for filepath in files:
            fname = os.path.basename(filepath)
            self.stdout.write(f"\n[{fname}]")
            l, e = _import_file(filepath, self.stdout, self.style, flush=flush)
            self.stdout.write(self.style.SUCCESS(f"  +{l} leçons, +{e} exercices"))
            total_lessons += l
            total_exercises += e

        self.stdout.write(self.style.SUCCESS(
            f"\nTOTAL : {total_lessons} leçons, {total_exercises} exercices importés."
        ))
