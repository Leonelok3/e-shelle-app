# Generated manually for E-Shelle Jobs.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SecteurJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=80)),
                ("slug", models.SlugField(blank=True, max_length=100, unique=True)),
                ("active", models.BooleanField(default=True)),
                ("ordre", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Secteur",
                "verbose_name_plural": "Secteurs",
                "ordering": ["ordre", "nom"],
            },
        ),
        migrations.CreateModel(
            name="VilleJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=80)),
                ("slug", models.SlugField(blank=True, max_length=100, unique=True)),
                ("region", models.CharField(blank=True, max_length=80)),
                ("active", models.BooleanField(default=True)),
                ("ordre", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Ville",
                "verbose_name_plural": "Villes",
                "ordering": ["ordre", "nom"],
            },
        ),
        migrations.CreateModel(
            name="OffreJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titre", models.CharField(max_length=160)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("entreprise", models.CharField(max_length=140)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="jobs/logos/")),
                ("quartier", models.CharField(blank=True, max_length=120)),
                ("type_contrat", models.CharField(choices=[("CDI", "CDI"), ("CDD", "CDD"), ("STAGE", "Stage"), ("MISSION", "Mission"), ("JOURNALIER", "Journalier"), ("FREELANCE", "Freelance")], default="CDI", max_length=20)),
                ("mode_travail", models.CharField(choices=[("SUR_SITE", "Sur site"), ("HYBRIDE", "Hybride"), ("DISTANCE", "A distance")], default="SUR_SITE", max_length=20)),
                ("salaire_min", models.PositiveIntegerField(blank=True, null=True)),
                ("salaire_max", models.PositiveIntegerField(blank=True, null=True)),
                ("devise", models.CharField(default="XAF", max_length=10)),
                ("description", models.TextField()),
                ("missions", models.TextField(blank=True)),
                ("profil_recherche", models.TextField(blank=True)),
                ("avantages", models.TextField(blank=True)),
                ("telephone", models.CharField(blank=True, max_length=30)),
                ("whatsapp", models.CharField(blank=True, help_text="Numero WhatsApp sans +, ex: 237680625082", max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("lien_externe", models.URLField(blank=True)),
                ("date_limite", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=False)),
                ("is_verified", models.BooleanField(default=False)),
                ("is_featured", models.BooleanField(default=False)),
                ("vues", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("auteur", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="offres_jobs", to=settings.AUTH_USER_MODEL)),
                ("secteur", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="offres", to="jobs.secteurjob")),
                ("ville", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="offres", to="jobs.villejob")),
            ],
            options={
                "verbose_name": "Offre d'emploi",
                "verbose_name_plural": "Offres d'emploi",
                "ordering": ["-is_featured", "-is_verified", "-created_at"],
                "indexes": [
                    models.Index(fields=["is_active", "type_contrat", "created_at"], name="jobs_offrej_is_acti_d90815_idx"),
                    models.Index(fields=["ville", "secteur", "is_active"], name="jobs_offrej_ville_i_5c1093_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="CandidatureJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=140)),
                ("telephone", models.CharField(max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("ville", models.CharField(blank=True, max_length=80)),
                ("message", models.TextField(blank=True)),
                ("cv", models.FileField(blank=True, null=True, upload_to="jobs/cv/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("offre", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="candidatures", to="jobs.offrejob")),
            ],
            options={
                "verbose_name": "Candidature",
                "verbose_name_plural": "Candidatures",
                "ordering": ["-created_at"],
            },
        ),
    ]
