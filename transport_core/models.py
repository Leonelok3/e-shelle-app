import urllib.parse
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class VilleTransport(models.Model):
    nom = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    region = models.CharField(max_length=80, blank=True)
    active = models.BooleanField(default=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "Ville"
        verbose_name_plural = "Villes"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)[:100]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Trajet(models.Model):
    class TypeTrajet(models.TextChoices):
        COVOITURAGE = "COVOITURAGE", "Covoiturage"
        BUS = "BUS", "Bus"
        TAXI = "TAXI", "Taxi"
        COLIS = "COLIS", "Colis"

    class Statut(models.TextChoices):
        OUVERT = "OUVERT", "Ouvert"
        COMPLET = "COMPLET", "Complet"
        ANNULE = "ANNULE", "Annule"

    titre = models.CharField(max_length=160)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    type_trajet = models.CharField(max_length=20, choices=TypeTrajet.choices, default=TypeTrajet.COVOITURAGE)
    depart = models.ForeignKey(VilleTransport, on_delete=models.PROTECT, related_name="departs")
    arrivee = models.ForeignKey(VilleTransport, on_delete=models.PROTECT, related_name="arrivees")
    lieu_depart = models.CharField(max_length=160, blank=True)
    lieu_arrivee = models.CharField(max_length=160, blank=True)
    date_depart = models.DateField()
    heure_depart = models.TimeField()
    places_disponibles = models.PositiveIntegerField(default=1)
    prix_place = models.PositiveIntegerField(default=0)
    devise = models.CharField(max_length=10, default="XAF")
    conducteur_nom = models.CharField(max_length=120)
    telephone = models.CharField(max_length=30)
    whatsapp = models.CharField(max_length=30, blank=True, help_text="Numero WhatsApp sans +, ex: 237680625082")
    vehicule = models.CharField(max_length=120, blank=True)
    bagages_acceptes = models.BooleanField(default=True)
    colis_acceptes = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    conditions = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.OUVERT)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    vues = models.PositiveIntegerField(default=0)
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="trajets_transport")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "date_depart", "heure_depart"]
        indexes = [
            models.Index(fields=["is_active", "statut", "date_depart"]),
            models.Index(fields=["depart", "arrivee", "date_depart"]),
        ]
        verbose_name = "Trajet"
        verbose_name_plural = "Trajets"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.depart}-{self.arrivee}-{self.date_depart}-{self.conducteur_nom}")[:190] or "trajet"
            slug, n = base, 1
            while Trajet.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"[:220]
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.depart} -> {self.arrivee} ({self.date_depart})"

    def get_absolute_url(self):
        return reverse("transport:detail", kwargs={"slug": self.slug})

    @property
    def prix_display(self):
        if not self.prix_place:
            return "Prix a discuter"
        return f"{self.prix_place:,} {self.devise}".replace(",", " ")

    @property
    def est_passe(self):
        return self.date_depart < timezone.localdate()

    @property
    def whatsapp_url(self):
        numero = (self.whatsapp or self.telephone).replace("+", "").replace(" ", "").replace("-", "")
        msg = f"Bonjour, je veux reserver une place pour {self.depart} -> {self.arrivee} le {self.date_depart} via E-Shelle Transport."
        return f"https://wa.me/{numero}?text={urllib.parse.quote(msg)}"

    @property
    def tel_url(self):
        return f"tel:{self.telephone}"


class DemandeTrajet(models.Model):
    depart = models.ForeignKey(VilleTransport, on_delete=models.PROTECT, related_name="demandes_depart")
    arrivee = models.ForeignKey(VilleTransport, on_delete=models.PROTECT, related_name="demandes_arrivee")
    date_souhaitee = models.DateField()
    nom = models.CharField(max_length=120)
    telephone = models.CharField(max_length=30)
    places = models.PositiveIntegerField(default=1)
    budget_max = models.PositiveIntegerField(null=True, blank=True)
    message = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_souhaitee", "-created_at"]
        verbose_name = "Demande de trajet"
        verbose_name_plural = "Demandes de trajet"

    def __str__(self):
        return f"{self.nom}: {self.depart} -> {self.arrivee}"
