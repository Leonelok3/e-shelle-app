# Generated manually for E-Shelle Transport.

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
            name="VilleTransport",
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
            name="DemandeTrajet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_souhaitee", models.DateField()),
                ("nom", models.CharField(max_length=120)),
                ("telephone", models.CharField(max_length=30)),
                ("places", models.PositiveIntegerField(default=1)),
                ("budget_max", models.PositiveIntegerField(blank=True, null=True)),
                ("message", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("arrivee", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="demandes_arrivee", to="transport_core.villetransport")),
                ("depart", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="demandes_depart", to="transport_core.villetransport")),
            ],
            options={
                "verbose_name": "Demande de trajet",
                "verbose_name_plural": "Demandes de trajet",
                "ordering": ["date_souhaitee", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Trajet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titre", models.CharField(max_length=160)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("type_trajet", models.CharField(choices=[("COVOITURAGE", "Covoiturage"), ("BUS", "Bus"), ("TAXI", "Taxi"), ("COLIS", "Colis")], default="COVOITURAGE", max_length=20)),
                ("lieu_depart", models.CharField(blank=True, max_length=160)),
                ("lieu_arrivee", models.CharField(blank=True, max_length=160)),
                ("date_depart", models.DateField()),
                ("heure_depart", models.TimeField()),
                ("places_disponibles", models.PositiveIntegerField(default=1)),
                ("prix_place", models.PositiveIntegerField(default=0)),
                ("devise", models.CharField(default="XAF", max_length=10)),
                ("conducteur_nom", models.CharField(max_length=120)),
                ("telephone", models.CharField(max_length=30)),
                ("whatsapp", models.CharField(blank=True, help_text="Numero WhatsApp sans +, ex: 237680625082", max_length=30)),
                ("vehicule", models.CharField(blank=True, max_length=120)),
                ("bagages_acceptes", models.BooleanField(default=True)),
                ("colis_acceptes", models.BooleanField(default=False)),
                ("description", models.TextField(blank=True)),
                ("conditions", models.TextField(blank=True)),
                ("statut", models.CharField(choices=[("OUVERT", "Ouvert"), ("COMPLET", "Complet"), ("ANNULE", "Annule")], default="OUVERT", max_length=20)),
                ("is_active", models.BooleanField(default=False)),
                ("is_verified", models.BooleanField(default=False)),
                ("is_featured", models.BooleanField(default=False)),
                ("vues", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("arrivee", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="arrivees", to="transport_core.villetransport")),
                ("auteur", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="trajets_transport", to=settings.AUTH_USER_MODEL)),
                ("depart", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="departs", to="transport_core.villetransport")),
            ],
            options={
                "verbose_name": "Trajet",
                "verbose_name_plural": "Trajets",
                "ordering": ["-is_featured", "date_depart", "heure_depart"],
                "indexes": [
                    models.Index(fields=["is_active", "statut", "date_depart"], name="transport_c_is_acti_fb363e_idx"),
                    models.Index(fields=["depart", "arrivee", "date_depart"], name="transport_c_depart__e76132_idx"),
                ],
            },
        ),
    ]
