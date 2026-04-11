"""
setup_french_exams.py — Crée les Exam + ExamSection de base pour le module français.
Usage : python manage.py setup_french_exams
"""
from django.core.management.base import BaseCommand
from preparation_tests.models import Exam, ExamSection

EXAMS = [
    {"code": "tef",  "name": "TEF — Test d'Évaluation de Français",    "language": "fr"},
    {"code": "tcf",  "name": "TCF — Test de Connaissance du Français",  "language": "fr"},
    {"code": "delf", "name": "DELF — Diplôme d'Études en Langue Française", "language": "fr"},
    {"code": "dalf", "name": "DALF — Diplôme Approfondi de Langue Française", "language": "fr"},
]

SECTIONS = [
    {"code": "co", "order": 1, "duration_sec": 1800},
    {"code": "ce", "order": 2, "duration_sec": 1800},
    {"code": "ee", "order": 3, "duration_sec": 2400},
    {"code": "eo", "order": 4, "duration_sec": 1200},
]


class Command(BaseCommand):
    help = "Crée les Exam + ExamSection TEF/TCF/DELF/DALF si inexistants."

    def handle(self, *args, **options):
        for ed in EXAMS:
            exam, created = Exam.objects.get_or_create(
                code=ed["code"],
                defaults={"name": ed["name"], "language": ed["language"]},
            )
            status = "créé" if created else "déjà présent"
            self.stdout.write(f"  {ed['code'].upper()} — {status}")

            for sd in SECTIONS:
                _, s_created = ExamSection.objects.get_or_create(
                    exam=exam, code=sd["code"],
                    defaults={"order": sd["order"], "duration_sec": sd["duration_sec"]},
                )

        self.stdout.write(self.style.SUCCESS("✅ Examens français configurés."))
