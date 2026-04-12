"""
pressing/models.py — E-Shelle Pressing
Plateforme de pressing & blanchisserie au Cameroun.
Le client commande en ligne, le pressing collecte et livre.
"""
import urllib.parse
from datetime import date, timedelta
from django.db import models
from django.utils.text import slugify
from django.conf import settings


# ─── Référentiels géo ─────────────────────────────────────────────────────────

class VillePressing(models.Model):
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


class QuartierPressing(models.Model):
    ville  = models.ForeignKey(VillePressing, on_delete=models.CASCADE, related_name="quartiers")
    nom    = models.CharField(max_length=100)
    slug   = models.SlugField(max_length=120, unique=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.ville.slug}-{self.nom}")[:120]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.ville.nom})"


# ─── Catégories de service ────────────────────────────────────────────────────

class CategoriePressing(models.Model):
    nom    = models.CharField(max_length=100)
    slug   = models.SlugField(max_length=120, unique=True, blank=True)
    icone  = models.CharField(max_length=10, default="👔")
    ordre  = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories de pressing"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


# ─── Établissement pressing ───────────────────────────────────────────────────

class Pressing(models.Model):
    """Pressing / blanchisserie inscrit sur la plateforme."""

    # Identité
    nom         = models.CharField(max_length=150)
    slug        = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    photo       = models.ImageField(upload_to="pressing/photos/", null=True, blank=True)
    logo        = models.ImageField(upload_to="pressing/logos/",  null=True, blank=True)
    gerant      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                    null=True, blank=True, related_name="pressings")

    # Localisation
    ville     = models.ForeignKey(VillePressing, on_delete=models.PROTECT, related_name="pressings")
    quartier  = models.ForeignKey(QuartierPressing, on_delete=models.SET_NULL,
                  null=True, blank=True, related_name="pressings")
    adresse   = models.CharField(max_length=250, blank=True)
    zone_livraison = models.TextField(blank=True,
                      help_text="Quartiers couverts par la collecte/livraison")

    # Contact
    telephone    = models.CharField(max_length=20)
    whatsapp     = models.CharField(max_length=20, blank=True,
                    help_text="Sans +, ex: 237680625082")
    whatsapp_msg = models.CharField(max_length=300, blank=True)

    # Catégories de services proposés
    categories = models.ManyToManyField(CategoriePressing, blank=True, related_name="pressings")

    # Service
    horaires          = models.CharField(max_length=200, default="Lun-Sam 8h-19h")
    collecte_domicile = models.BooleanField(default=False,
                         help_text="Collecte des vêtements à domicile")
    livraison_domicile = models.BooleanField(default=False,
                          help_text="Livraison des vêtements traités à domicile")
    delai_traitement  = models.CharField(max_length=60, default="24-48h",
                          help_text="Délai de traitement habituel")
    delai_livraison   = models.CharField(max_length=60, blank=True,
                          help_text="Délai de livraison à domicile")
    express           = models.BooleanField(default=False,
                          help_text="Service express disponible (même jour)")

    # Souscription mensuelle
    PLAN_CHOICES = [
        ("basic",   "Basic — 2 000 FCFA/mois"),
        ("pro",     "Pro — 5 000 FCFA/mois"),
        ("premium", "Premium — 10 000 FCFA/mois"),
    ]
    plan_actif           = models.CharField(max_length=10, choices=PLAN_CHOICES,
                            null=True, blank=True)
    abonnement_actif     = models.BooleanField(default=False)
    abonnement_expire_le = models.DateField(null=True, blank=True)
    montant_paye         = models.PositiveIntegerField(null=True, blank=True)
    ref_paiement         = models.CharField(max_length=100, blank=True)
    notes_admin          = models.TextField(blank=True)

    # Statut
    is_active   = models.BooleanField(default=False,
                    help_text="Visible après confirmation du paiement")
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    note_moyenne = models.FloatField(default=0.0)
    nb_avis      = models.PositiveIntegerField(default=0)
    nb_vues      = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-is_verified", "nom"]
        verbose_name = "Pressing"
        verbose_name_plural = "Pressings"

    def save(self, *args, **kwargs):
        if not self.slug:
            ville_nom = self.ville.nom if self.ville_id else "pressing"
            base = slugify(f"{self.nom}-{ville_nom}")
            slug, n = base, 1
            while Pressing.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug[:200]
        if not self.whatsapp_msg:
            self.whatsapp_msg = "Bonjour, je voudrais commander un service de pressing."
        if self.abonnement_actif and self.abonnement_expire_le:
            if self.abonnement_expire_le < date.today():
                self.abonnement_actif = False
                self.is_active = False
        super().save(*args, **kwargs)

    @property
    def jours_restants(self):
        if self.abonnement_expire_le:
            return max(0, (self.abonnement_expire_le - date.today()).days)
        return 0

    @property
    def whatsapp_url(self):
        numero = (self.whatsapp or self.telephone).replace(" ", "").replace("+", "")
        msg = self.whatsapp_msg or "Bonjour, je voudrais un service de pressing."
        return f"https://wa.me/{numero}?text={urllib.parse.quote(msg)}"

    @property
    def tel_url(self):
        return f"tel:{self.telephone}"

    @property
    def etoiles(self):
        return round(self.note_moyenne)

    def whatsapp_commande_url(self, articles_text: str):
        numero = (self.whatsapp or self.telephone).replace(" ", "").replace("+", "")
        msg = f"Bonjour {self.nom}, je voudrais déposer une commande pressing :\n{articles_text}\nMerci de confirmer le prix et le délai."
        return f"https://wa.me/{numero}?text={urllib.parse.quote(msg)}"


# ─── Services / Tarifs ────────────────────────────────────────────────────────

class ServicePressing(models.Model):
    """Un article/service avec son prix dans un pressing."""
    UNITE_CHOICES = [
        ("piece",  "À la pièce"),
        ("kg",     "Au kilogramme"),
        ("lot",    "Au lot"),
        ("forfait","Forfait"),
    ]

    pressing   = models.ForeignKey(Pressing, on_delete=models.CASCADE, related_name="services")
    categorie  = models.ForeignKey(CategoriePressing, on_delete=models.SET_NULL,
                   null=True, blank=True, related_name="services")
    nom        = models.CharField(max_length=150, help_text="Ex: Chemise homme, Costume 2 pièces")
    icone      = models.CharField(max_length=10, default="👔")
    prix       = models.PositiveIntegerField(help_text="Prix en FCFA")
    unite      = models.CharField(max_length=10, choices=UNITE_CHOICES, default="piece")
    disponible = models.BooleanField(default=True)
    ordre      = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["categorie", "ordre", "nom"]
        verbose_name = "Service / Tarif"
        verbose_name_plural = "Services & Tarifs"

    def __str__(self):
        return f"{self.nom} — {self.prix} FCFA/{self.get_unite_display()}"

    @property
    def prix_display(self):
        return f"{self.prix:,} FCFA/{self.get_unite_display()}".replace(",", " ")


# ─── Commandes ────────────────────────────────────────────────────────────────

class CommandePressing(models.Model):
    """Commande client passée via la plateforme."""

    STATUT_CHOICES = [
        ("en_attente",  "En attente de confirmation"),
        ("confirme",    "Confirmée"),
        ("en_cours",    "En cours de traitement"),
        ("pret",        "Prêt — à récupérer / à livrer"),
        ("livre",       "Livré / Récupéré"),
        ("annule",      "Annulée"),
    ]
    MODE_CHOICES = [
        ("depot",     "Je dépose au pressing"),
        ("collecte",  "Collecte à domicile"),
    ]

    pressing   = models.ForeignKey(Pressing, on_delete=models.CASCADE, related_name="commandes")
    client     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                   null=True, blank=True, related_name="commandes_pressing")
    # Info client (si non connecté)
    nom_client  = models.CharField(max_length=100, blank=True)
    tel_client  = models.CharField(max_length=20, blank=True)
    adresse_collecte = models.CharField(max_length=300, blank=True,
                         help_text="Adresse pour la collecte/livraison à domicile")

    mode        = models.CharField(max_length=10, choices=MODE_CHOICES, default="depot")
    articles    = models.JSONField(default=list,
                   help_text="Liste des articles : [{service_id, nom, qte, prix_unit}]")
    notes       = models.TextField(blank=True, help_text="Instructions spéciales")
    montant_total = models.PositiveIntegerField(default=0)

    statut      = models.CharField(max_length=15, choices=STATUT_CHOICES, default="en_attente")
    date_collecte = models.DateField(null=True, blank=True,
                      help_text="Date souhaitée pour la collecte ou le dépôt")
    date_pret     = models.DateField(null=True, blank=True,
                      help_text="Date estimée de fin de traitement")

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

    def __str__(self):
        client_str = self.client.username if self.client else self.nom_client or "Anonyme"
        return f"Cmd #{self.pk} — {self.pressing.nom} — {client_str}"

    @property
    def statut_color(self):
        return {
            "en_attente": "amber",
            "confirme":   "blue",
            "en_cours":   "indigo",
            "pret":       "green",
            "livre":      "gray",
            "annule":     "red",
        }.get(self.statut, "gray")

    @property
    def client_nom(self):
        if self.client:
            return self.client.get_full_name() or self.client.username
        return self.nom_client or "Client anonyme"

    def whatsapp_recap_url(self):
        """Lien WhatsApp avec récap de commande pour le pressing."""
        numero = (self.pressing.whatsapp or self.pressing.telephone).replace(" ", "").replace("+", "")
        articles_str = "\n".join(
            f"  - {a.get('nom','?')} x{a.get('qte',1)} = {a.get('prix_unit',0)*a.get('qte',1):,} FCFA"
            for a in (self.articles or [])
        )
        msg = (
            f"Bonjour {self.pressing.nom}, voici ma commande :\n"
            f"{articles_str}\n"
            f"Total : {self.montant_total:,} FCFA\n"
            f"Mode : {self.get_mode_display()}\n"
            f"{'Adresse : ' + self.adresse_collecte if self.adresse_collecte else ''}\n"
            f"{'Notes : ' + self.notes if self.notes else ''}"
        ).strip()
        return f"https://wa.me/{numero}?text={urllib.parse.quote(msg)}"


# ─── Avis clients ─────────────────────────────────────────────────────────────

class AvisPressing(models.Model):
    pressing    = models.ForeignKey(Pressing, on_delete=models.CASCADE, related_name="avis")
    auteur      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                    related_name="avis_pressing")
    note        = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    commentaire = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("pressing", "auteur")
        ordering = ["-created_at"]
        verbose_name = "Avis"
        verbose_name_plural = "Avis"

    def __str__(self):
        return f"{self.auteur.username} → {self.pressing.nom} ({self.note}★)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        avis = AvisPressing.objects.filter(pressing=self.pressing)
        self.pressing.note_moyenne = avis.aggregate(
            m=models.Avg("note"))["m"] or 0.0
        self.pressing.nb_avis = avis.count()
        self.pressing.save(update_fields=["note_moyenne", "nb_avis"])
