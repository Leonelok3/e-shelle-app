# Generated manually for E-Shelle Santé Pro.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sante", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NumeroUrgenceSante",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=120)),
                ("categorie", models.CharField(default="Urgence", max_length=80)),
                ("telephone", models.CharField(max_length=30)),
                ("description", models.CharField(blank=True, max_length=220)),
                ("disponible_24h", models.BooleanField(default=True)),
                ("ordre", models.PositiveIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
                ("ville", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="numeros_urgence", to="sante.villesante")),
            ],
            options={
                "verbose_name": "Numéro d'urgence santé",
                "verbose_name_plural": "Numéros d'urgence santé",
                "ordering": ["ordre", "nom"],
            },
        ),
        migrations.CreateModel(
            name="ImageProduitSante",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="sante/produits/galerie/")),
                ("legende", models.CharField(blank=True, max_length=160)),
                ("ordre", models.PositiveIntegerField(default=0)),
                ("produit", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="sante.produitsante")),
            ],
            options={
                "verbose_name": "Image produit santé",
                "verbose_name_plural": "Images produits santé",
                "ordering": ["ordre", "id"],
            },
        ),
        migrations.CreateModel(
            name="RendezVousSante",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=120)),
                ("telephone", models.CharField(max_length=30)),
                ("motif", models.CharField(max_length=180)),
                ("date_souhaitee", models.DateField()),
                ("heure_souhaitee", models.TimeField(blank=True, null=True)),
                ("message", models.TextField(blank=True)),
                ("statut", models.CharField(choices=[("NOUVEAU", "Nouveau"), ("CONFIRME", "Confirmé"), ("TERMINE", "Terminé"), ("ANNULE", "Annulé")], default="NOUVEAU", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("professionnel", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rendez_vous", to="sante.professionnelsante")),
            ],
            options={
                "verbose_name": "Rendez-vous santé",
                "verbose_name_plural": "Rendez-vous santé",
                "ordering": ["-created_at"],
            },
        ),
    ]
