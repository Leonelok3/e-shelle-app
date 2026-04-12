"""
pharma/models.py — E-Shelle Pharma
Annuaire de pharmacies + disponibilité médicaments au Cameroun.
Le client trouve la pharmacie, contacte par WhatsApp/appel, paie sur place.
"""
import urllib.parse
from datetime import date
from django.db import models
from django.utils.text import slugify
from django.conf import settings


# ─── Référentiels géographiques ───────────────────────────────────────────────

class VillePharma(models.Model):
    nom    = models.CharField(max_length=80)
    slug   = models.SlugField(max_length=100, unique=True, blank=True)
    region = models.CharField(max_length=80, default="Centre")
    active = models.BooleanField(default=True)
    ordre  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "Ville"
        verbose_name_plural = "Villes"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class QuartierPharma(models.Model):
    ville  = models.ForeignKey(VillePharma, on_delete=models.CASCADE, related_name="quartiers")
    nom    = models.CharField(max_length=100)
    slug   = models.SlugField(max_length=120, unique=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.ville.slug}-{self.nom}")
            self.slug = base[:120]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.ville.nom})"


# ─── Médicaments ──────────────────────────────────────────────────────────────

class CategorieMedicament(models.Model):
    nom    = models.CharField(max_length=100)
    slug   = models.SlugField(max_length=120, unique=True, blank=True)
    icone  = models.CharField(max_length=10, default="💊")
    ordre  = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories de médicaments"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Medicament(models.Model):
    """Médicament générique — indépendant des pharmacies."""
    nom         = models.CharField(max_length=200, help_text="Nom générique ou commercial")
    slug        = models.SlugField(max_length=250, unique=True, blank=True)
    categorie   = models.ForeignKey(CategorieMedicament, on_delete=models.SET_NULL,
                    null=True, blank=True, related_name="medicaments")
    description = models.TextField(blank=True,
                    help_text="Indications, posologie générale")
    image       = models.ImageField(upload_to="pharma/medicaments/", null=True, blank=True)
    ordonnance  = models.BooleanField(default=False,
                    help_text="Médicament sur ordonnance uniquement")
    actif       = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "Médicament"
        verbose_name_plural = "Médicaments"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nom)
            slug, n = base[:245], 1
            while Medicament.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base[:240]}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    @property
    def nb_pharmacies(self):
        return self.stocks.filter(disponible=True,
                                  pharmacie__is_active=True,
                                  pharmacie__abonnement_actif=True).count()


# ─── Pharmacies ───────────────────────────────────────────────────────────────

class Pharmacie(models.Model):
    """Pharmacie inscrite sur la plateforme."""

    # Identité
    nom         = models.CharField(max_length=150)
    slug        = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    photo       = models.ImageField(upload_to="pharma/pharmacies/", null=True, blank=True)
    gerant      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                    null=True, blank=True, related_name="pharmacies")

    # Localisation
    ville          = models.ForeignKey(VillePharma, on_delete=models.PROTECT, related_name="pharmacies")
    quartier       = models.ForeignKey(QuartierPharma, on_delete=models.SET_NULL,
                        null=True, blank=True, related_name="pharmacies")
    adresse        = models.CharField(max_length=250, blank=True)

    # Contact
    telephone    = models.CharField(max_length=20)
    whatsapp     = models.CharField(max_length=20, blank=True,
                    help_text="Numéro sans +, ex: 237680625082")
    whatsapp_msg = models.CharField(max_length=300, blank=True)

    # Service
    horaires         = models.CharField(max_length=200, default="Lun-Sam 8h-20h")
    garde            = models.BooleanField(default=False,
                        help_text="Pharmacie de garde (ouverte nuit/weekend)")
    garde_info       = models.CharField(max_length=200, blank=True,
                        help_text="Ex: Garde du 12 au 15 avril")
    livraison        = models.BooleanField(default=False,
                        help_text="Livraison à domicile disponible")
    delai_livraison  = models.CharField(max_length=60, blank=True, default="")

    # Souscription mensuelle
    PLAN_CHOICES = [
        ("basic",   "Basic — 2 000 FCFA/mois"),
        ("pro",     "Pro — 5 000 FCFA/mois"),
        ("premium", "Premium — 10 000 FCFA/mois"),
    ]
    plan_actif           = models.CharField(max_length=10, choices=PLAN_CHOICES,
                            null=True, blank=True, verbose_name="Plan souscrit")
    abonnement_actif     = models.BooleanField(default=False,
                            help_text="Visible sur la plateforme après paiement")
    abonnement_expire_le = models.DateField(null=True, blank=True)
    montant_paye         = models.PositiveIntegerField(null=True, blank=True)
    ref_paiement         = models.CharField(max_length=100, blank=True)
    notes_admin          = models.TextField(blank=True)

    # Statut
    is_active   = models.BooleanField(default=False,
                    help_text="Activer après confirmation du paiement")
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    note_moyenne = models.FloatField(default=0.0)
    nb_avis      = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-is_verified", "nom"]
        verbose_name = "Pharmacie"
        verbose_name_plural = "Pharmacies"

    def save(self, *args, **kwargs):
        if not self.slug:
            ville_nom = self.ville.nom if self.ville_id else "pharma"
            base = slugify(f"{self.nom}-{ville_nom}")
            slug, n = base, 1
            while Pharmacie.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug[:200]
        if not self.whatsapp_msg:
            self.whatsapp_msg = "Bonjour, je voudrais savoir si vous avez un médicament en stock."
        # Auto-expiration abonnement
        if self.abonnement_actif and self.abonnement_expire_le:
            if self.abonnement_expire_le < date.today():
                self.abonnement_actif = False
                self.is_active = False
        super().save(*args, **kwargs)

    @property
    def abonnement_expire(self):
        if self.abonnement_expire_le:
            return self.abonnement_expire_le < date.today()
        return True

    @property
    def jours_restants(self):
        if self.abonnement_expire_le:
            return max(0, (self.abonnement_expire_le - date.today()).days)
        return 0

    @property
    def whatsapp_url(self):
        numero = (self.whatsapp or self.telephone).replace(" ", "").replace("+", "")
        msg = self.whatsapp_msg or "Bonjour, je cherche un médicament."
        return f"https://wa.me/{numero}?text={urllib.parse.quote(msg)}"

    def whatsapp_url_medicament(self, medicament_nom):
        numero = (self.whatsapp or self.telephone).replace(" ", "").replace("+", "")
        msg = f"Bonjour, avez-vous {medicament_nom} en stock ? Quel est le prix ?"
        return f"https://wa.me/{numero}?text={urllib.parse.quote(msg)}"

    @property
    def tel_url(self):
        return f"tel:{self.telephone}"

    @property
    def etoiles(self):
        return round(self.note_moyenne)

    @property
    def nb_medicaments_dispo(self):
        return self.stocks.filter(disponible=True).count()


# ─── Stock pharmacie ↔ médicament ────────────────────────────────────────────

class StockPharmacie(models.Model):
    """Disponibilité et prix d'un médicament dans une pharmacie."""
    pharmacie  = models.ForeignKey(Pharmacie, on_delete=models.CASCADE, related_name="stocks")
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE, related_name="stocks")
    prix       = models.PositiveIntegerField(null=True, blank=True,
                    help_text="Prix en FCFA (laisser vide si prix variable)")
    disponible = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("pharmacie", "medicament")
        ordering = ["medicament__nom"]
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

    def __str__(self):
        dispo = "✓" if self.disponible else "✗"
        prix_str = f"{self.prix} FCFA" if self.prix else "prix N/C"
        return f"{dispo} {self.medicament.nom} @ {self.pharmacie.nom} ({prix_str})"


# ─── Avis clients ─────────────────────────────────────────────────────────────

class AvisPharmacie(models.Model):
    pharmacie   = models.ForeignKey(Pharmacie, on_delete=models.CASCADE, related_name="avis")
    auteur      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                    related_name="avis_pharma")
    note        = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    commentaire = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("pharmacie", "auteur")
        ordering = ["-created_at"]
        verbose_name = "Avis"
        verbose_name_plural = "Avis"

    def __str__(self):
        return f"{self.auteur.username} → {self.pharmacie.nom} ({self.note}★)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        avis = AvisPharmacie.objects.filter(pharmacie=self.pharmacie)
        self.pharmacie.note_moyenne = avis.aggregate(
            m=models.Avg("note"))["m"] or 0.0
        self.pharmacie.nb_avis = avis.count()
        self.pharmacie.save(update_fields=["note_moyenne", "nb_avis"])
