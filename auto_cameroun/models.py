"""
models.py — auto_cameroun
Marketplace automobile Cameroun : vente & location de véhicules
"""
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
import uuid


# ─────────────────────────────────────────────────────────────────
# CHOIX
# ─────────────────────────────────────────────────────────────────

class TypeTransaction(models.TextChoices):
    VENTE    = "VENTE",    "Vente"
    LOCATION = "LOCATION", "Location"

class StatutVehicule(models.TextChoices):
    BROUILLON            = "BROUILLON",            "Brouillon"
    EN_ATTENTE_VALIDATION = "EN_ATTENTE_VALIDATION", "En attente de validation"
    PUBLIE               = "PUBLIE",               "Publié"
    RESERVE              = "RESERVE",              "Réservé"
    VENDU_LOUE           = "VENDU_LOUE",           "Vendu / Loué"
    REFUSE               = "REFUSE",               "Refusé"
    ARCHIVE              = "ARCHIVE",              "Archivé"

class TypeCarburant(models.TextChoices):
    ESSENCE  = "ESSENCE",  "Essence"
    DIESEL   = "DIESEL",   "Diesel"
    HYBRIDE  = "HYBRIDE",  "Hybride"
    ELECTRIQUE = "ELECTRIQUE", "Électrique"
    GPL      = "GPL",      "GPL"
    AUTRE    = "AUTRE",    "Autre"

class TypeBoite(models.TextChoices):
    MANUELLE    = "MANUELLE",    "Manuelle"
    AUTOMATIQUE = "AUTOMATIQUE", "Automatique"
    SEMI_AUTO   = "SEMI_AUTO",   "Semi-automatique"

class TypeCarrosserie(models.TextChoices):
    BERLINE     = "BERLINE",     "Berline"
    SUV         = "SUV",         "SUV / 4x4"
    PICKUP      = "PICKUP",      "Pick-up"
    MINIBUS     = "MINIBUS",     "Minibus"
    CAMION      = "CAMION",      "Camion"
    MOTO        = "MOTO",        "Moto"
    BUS         = "BUS",         "Bus"
    UTILITAIRE  = "UTILITAIRE",  "Utilitaire"
    COUPE       = "COUPE",       "Coupé"
    CABRIOLET   = "CABRIOLET",   "Cabriolet"
    BREAK       = "BREAK",       "Break"
    AUTRE       = "AUTRE",       "Autre"

class TypeConduite(models.TextChoices):
    GAUCHE = "GAUCHE", "Volant à gauche"
    DROITE = "DROITE", "Volant à droite"

class EtatVehicule(models.TextChoices):
    NEUF          = "NEUF",          "Neuf"
    EXCELLENT     = "EXCELLENT",     "Excellent état"
    TRES_BON      = "TRES_BON",      "Très bon état"
    BON           = "BON",           "Bon état"
    PASSABLE      = "PASSABLE",      "État passable"
    POUR_PIECES   = "POUR_PIECES",   "Pour pièces"

class DeviseAuto(models.TextChoices):
    XAF = "XAF", "XAF (FCFA)"
    USD = "USD", "USD ($)"
    EUR = "EUR", "EUR (€)"

class PeriodePrixAuto(models.TextChoices):
    PAR_JOUR  = "PAR_JOUR",  "Par jour"
    PAR_MOIS  = "PAR_MOIS",  "Par mois"
    GLOBAL    = "GLOBAL",    "Prix global"


# ─────────────────────────────────────────────────────────────────
# PROFIL AUTO
# ─────────────────────────────────────────────────────────────────

class RoleVendeur(models.TextChoices):
    PARTICULIER = "PARTICULIER", "Particulier"
    CONCESSIONNAIRE = "CONCESSIONNAIRE", "Concessionnaire"
    GARAGE      = "GARAGE",      "Garage / Mécanicien"
    LOUEUR      = "LOUEUR",      "Loueur professionnel"

class TypeCompteAuto(models.TextChoices):
    FREE    = "FREE",    "Gratuit (3 annonces)"
    PREMIUM = "PREMIUM", "Premium (illimité)"


class ProfilAuto(models.Model):
    user        = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="profil_auto"
    )
    role        = models.CharField(max_length=20, choices=RoleVendeur.choices, default=RoleVendeur.PARTICULIER)
    compte_type = models.CharField(max_length=10, choices=TypeCompteAuto.choices, default=TypeCompteAuto.FREE)
    telephone   = models.CharField(max_length=20, blank=True)
    ville       = models.CharField(max_length=100, blank=True)
    photo_profil = models.ImageField(upload_to="auto/profils/", blank=True, null=True)
    description = models.TextField(blank=True)
    est_verifie = models.BooleanField(default=False)
    date_expiration_premium = models.DateField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil Auto"
        verbose_name_plural = "Profils Auto"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.get_role_display()}"

    @property
    def est_premium(self):
        if self.compte_type == TypeCompteAuto.PREMIUM:
            if self.date_expiration_premium is None:
                return True
            return self.date_expiration_premium >= timezone.now().date()
        return False

    @property
    def peut_publier(self):
        if self.est_premium:
            return True
        count = Vehicule.objects.filter(
            proprietaire=self.user,
            statut__in=[StatutVehicule.PUBLIE, StatutVehicule.EN_ATTENTE_VALIDATION, StatutVehicule.RESERVE]
        ).count()
        return count < getattr(settings, "AUTO_MAX_VEHICULES_GRATUIT", 3)


# ─────────────────────────────────────────────────────────────────
# VÉHICULE
# ─────────────────────────────────────────────────────────────────

class Vehicule(models.Model):
    # Identité
    proprietaire     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="vehicules"
    )
    slug             = models.SlugField(max_length=200, unique=True, blank=True)
    titre            = models.CharField(max_length=200)

    # Classification
    type_transaction = models.CharField(max_length=10, choices=TypeTransaction.choices, default=TypeTransaction.VENTE)
    type_carrosserie = models.CharField(max_length=20, choices=TypeCarrosserie.choices, default=TypeCarrosserie.BERLINE)
    etat             = models.CharField(max_length=20, choices=EtatVehicule.choices, default=EtatVehicule.BON)

    # Identité véhicule
    marque           = models.CharField(max_length=100)
    modele           = models.CharField(max_length=100)
    annee            = models.PositiveIntegerField(verbose_name="Année")
    version          = models.CharField(max_length=100, blank=True, verbose_name="Version / Finition")
    couleur          = models.CharField(max_length=50, blank=True)
    immatriculation  = models.CharField(max_length=30, blank=True, verbose_name="Immatriculation (optionnel)")

    # Motorisation
    carburant        = models.CharField(max_length=15, choices=TypeCarburant.choices, default=TypeCarburant.ESSENCE)
    boite            = models.CharField(max_length=15, choices=TypeBoite.choices, default=TypeBoite.MANUELLE)
    puissance_cv     = models.PositiveIntegerField(blank=True, null=True, verbose_name="Puissance (CV)")
    cylindree        = models.CharField(max_length=20, blank=True, verbose_name="Cylindrée")
    conduite         = models.CharField(max_length=10, choices=TypeConduite.choices, default=TypeConduite.GAUCHE)

    # Données
    kilometrage      = models.PositiveIntegerField(blank=True, null=True, verbose_name="Kilométrage")
    nombre_places    = models.PositiveSmallIntegerField(default=5, verbose_name="Nombre de places")
    nombre_portes    = models.PositiveSmallIntegerField(default=4, verbose_name="Nombre de portes")

    # Localisation
    ville            = models.CharField(max_length=100)
    quartier         = models.CharField(max_length=100, blank=True)
    adresse_complete = models.CharField(max_length=255, blank=True)

    # Prix
    prix             = models.DecimalField(max_digits=14, decimal_places=0)
    devise           = models.CharField(max_length=5, choices=DeviseAuto.choices, default=DeviseAuto.XAF)
    periode_prix     = models.CharField(max_length=15, choices=PeriodePrixAuto.choices, default=PeriodePrixAuto.GLOBAL)
    prix_negociable  = models.BooleanField(default=True, verbose_name="Prix négociable")

    # Description
    description      = models.TextField()
    options_equipements = models.TextField(blank=True, verbose_name="Options & équipements (liste libre)")

    # Statut / Mise en avant
    statut           = models.CharField(max_length=25, choices=StatutVehicule.choices, default=StatutVehicule.EN_ATTENTE_VALIDATION)
    est_mis_en_avant = models.BooleanField(default=False, verbose_name="Premium / En avant")
    est_coup_de_coeur = models.BooleanField(default=False, verbose_name="Coup de cœur")
    publie_par_admin = models.BooleanField(default=False)
    note_admin       = models.TextField(blank=True, verbose_name="Note interne admin")

    # Garantie / Dédouanement
    est_dedouane     = models.BooleanField(default=True, verbose_name="Dédouané")
    garantie         = models.CharField(max_length=100, blank=True, verbose_name="Garantie")
    premiere_main    = models.BooleanField(default=False, verbose_name="1ère main")

    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords    = models.CharField(max_length=200, blank=True)

    # Stats
    vues             = models.PositiveIntegerField(default=0)
    date_disponibilite = models.DateField(blank=True, null=True)
    date_publication = models.DateTimeField(blank=True, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ["-est_mis_en_avant", "-created_at"]

    def __str__(self):
        return f"{self.marque} {self.modele} {self.annee} — {self.ville}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.marque}-{self.modele}-{self.annee}-{self.ville}")
            slug = base
            n = 1
            while Vehicule.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        if not self.titre:
            self.titre = f"{self.marque} {self.modele} {self.annee}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("auto:detail_vehicule", kwargs={"slug": self.slug})

    @property
    def photo_principale(self):
        return self.photos.filter(est_photo_principale=True).first() or self.photos.first()

    @property
    def prix_formate(self):
        symboles = {"XAF": "XAF", "USD": "$", "EUR": "€"}
        sym = symboles.get(self.devise, self.devise)
        p = int(self.prix)
        if self.devise == "XAF":
            return f"{p:,} {sym}".replace(",", " ")
        return f"{p:,.0f} {sym}"

    # ── Partage réseaux sociaux ──────────────────────────────────

    def _url_absolue(self):
        try:
            from django.contrib.sites.models import Site
            domain = Site.objects.get_current().domain
        except Exception:
            domain = "e-shelle.com"
        return f"https://{domain}{self.get_absolute_url()}"

    def get_whatsapp_url(self):
        numero = getattr(settings, "AUTO_WHATSAPP_CONTACT", getattr(settings, "IMMO_WHATSAPP_CONTACT", "+237680625082"))
        msg = f"Bonjour, je suis intéressé(e) par ce véhicule : {self.marque} {self.modele} {self.annee} à {self.prix_formate} — {self._url_absolue()}"
        import urllib.parse
        return f"https://wa.me/{numero.replace('+', '')}?text={urllib.parse.quote(msg)}"

    def get_partage_facebook_url(self):
        import urllib.parse
        return f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(self._url_absolue())}"

    def get_partage_twitter_url(self):
        import urllib.parse
        texte = f"{self.marque} {self.modele} {self.annee} — {self.prix_formate} à {self.ville}"
        return f"https://twitter.com/intent/tweet?text={urllib.parse.quote(texte)}&url={urllib.parse.quote(self._url_absolue())}"

    def get_partage_linkedin_url(self):
        import urllib.parse
        return f"https://www.linkedin.com/sharing/share-offsite/?url={urllib.parse.quote(self._url_absolue())}"

    def get_partage_telegram_url(self):
        import urllib.parse
        texte = f"{self.marque} {self.modele} {self.annee} — {self.prix_formate}"
        return f"https://t.me/share/url?url={urllib.parse.quote(self._url_absolue())}&text={urllib.parse.quote(texte)}"


# ─────────────────────────────────────────────────────────────────
# PHOTO VÉHICULE
# ─────────────────────────────────────────────────────────────────

class PhotoVehicule(models.Model):
    vehicule           = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="photos")
    image              = models.ImageField(upload_to="auto/photos/")
    legende            = models.CharField(max_length=200, blank=True)
    est_photo_principale = models.BooleanField(default=False)
    ordre              = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "id"]
        verbose_name = "Photo véhicule"
        verbose_name_plural = "Photos véhicule"

    def __str__(self):
        return f"Photo {self.vehicule} — {self.legende or self.id}"


# ─────────────────────────────────────────────────────────────────
# DEMANDE D'ESSAI
# ─────────────────────────────────────────────────────────────────

class StatutDemandeEssai(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", "En attente"
    CONFIRME   = "CONFIRME",   "Confirmé"
    ANNULE     = "ANNULE",     "Annulé"
    EFFECTUE   = "EFFECTUE",   "Effectué"


class DemandeEssai(models.Model):
    vehicule      = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="demandes_essai")
    nom_complet   = models.CharField(max_length=150)
    telephone     = models.CharField(max_length=20)
    email         = models.EmailField(blank=True)
    date_souhaitee = models.DateField()
    message       = models.TextField(blank=True)
    statut        = models.CharField(max_length=15, choices=StatutDemandeEssai.choices, default=StatutDemandeEssai.EN_ATTENTE)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Demande d'essai"
        verbose_name_plural = "Demandes d'essai"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nom_complet} — {self.vehicule} — {self.date_souhaitee}"


# ─────────────────────────────────────────────────────────────────
# FAVORIS
# ─────────────────────────────────────────────────────────────────

class FavorisVehicule(models.Model):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favoris_auto")
    vehicule  = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="favoris")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "vehicule")
        verbose_name = "Favori véhicule"
        verbose_name_plural = "Favoris véhicules"

    def __str__(self):
        return f"{self.user} ❤️ {self.vehicule}"


# ─────────────────────────────────────────────────────────────────
# SIGNALEMENT
# ─────────────────────────────────────────────────────────────────

class MotifSignalementAuto(models.TextChoices):
    ARNAQUE      = "ARNAQUE",      "Arnaque / Fraude"
    DOUBLON      = "DOUBLON",      "Annonce dupliquée"
    PRIX_ABUSIF  = "PRIX_ABUSIF",  "Prix abusif"
    MAUVAISE_CAT = "MAUVAISE_CAT", "Mauvaise catégorie"
    PHOTOS_FAUSSES = "PHOTOS_FAUSSES", "Photos incorrectes / volées"
    AUTRE        = "AUTRE",        "Autre"


class SignalementVehicule(models.Model):
    vehicule   = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="signalements")
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    motif      = models.CharField(max_length=20, choices=MotifSignalementAuto.choices)
    description = models.TextField(blank=True)
    traite     = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Signalement véhicule"
        verbose_name_plural = "Signalements véhicules"

    def __str__(self):
        return f"Signalement {self.vehicule} — {self.motif}"


# ─────────────────────────────────────────────────────────────────
# SOUMISSION SANS COMPTE
# ─────────────────────────────────────────────────────────────────

class StatutSoumission(models.TextChoices):
    RECU          = "RECU",          "Reçu"
    EN_TRAITEMENT = "EN_TRAITEMENT", "En traitement"
    PUBLIE        = "PUBLIE",        "Publié"
    REJETE        = "REJETE",        "Rejeté"


class DemandeSoumissionVehicule(models.Model):
    """Formulaire de soumission sans compte utilisateur."""
    nom_complet       = models.CharField(max_length=150)
    telephone         = models.CharField(max_length=20)
    email             = models.EmailField(blank=True)
    marque            = models.CharField(max_length=100)
    modele            = models.CharField(max_length=100)
    annee             = models.PositiveIntegerField()
    type_transaction  = models.CharField(max_length=10, choices=TypeTransaction.choices, default=TypeTransaction.VENTE)
    ville             = models.CharField(max_length=100)
    prix              = models.DecimalField(max_digits=14, decimal_places=0, blank=True, null=True)
    description       = models.TextField(blank=True)
    statut            = models.CharField(max_length=15, choices=StatutSoumission.choices, default=StatutSoumission.RECU)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Soumission véhicule"
        verbose_name_plural = "Soumissions véhicules"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nom_complet} — {self.marque} {self.modele} {self.annee}"
