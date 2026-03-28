from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class TypeActeur(models.TextChoices):
    PRODUCTEUR      = 'producteur',     'Producteur / Agriculteur'
    ELEVEUR         = 'eleveur',        'Éleveur'
    TRANSFORMATEUR  = 'transformateur', 'Transformateur / Agroprocesseur'
    COOPERATIVE     = 'cooperative',    'Coopérative / GIC'
    EXPORTATEUR     = 'exportateur',    'Exportateur'
    GROSSISTE       = 'grossiste',      'Grossiste / Distributeur'
    IMPORTATEUR     = 'importateur',    'Importateur'
    GRANDE_SURFACE  = 'grande_surface', 'Grande Surface / Retail'
    COURTIER        = 'courtier',       'Courtier / Agent Commercial'
    RESTAURATEUR    = 'restaurateur',   'Restaurateur / HCR'
    INDUSTRIE       = 'industrie',      'Industrie Agroalimentaire'


class ActeurAgro(models.Model):
    """Profil professionnel lié au compte utilisateur existant (accounts.CustomUser)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profil_agro'
    )

    # Identité professionnelle
    type_acteur      = models.CharField(max_length=30, choices=TypeActeur.choices)
    nom_entreprise   = models.CharField(max_length=200)
    nom_contact      = models.CharField(max_length=100)
    poste_contact    = models.CharField(max_length=100, blank=True)
    logo             = models.ImageField(upload_to='agro/logos/%Y/', null=True, blank=True)
    photo_couverture = models.ImageField(upload_to='agro/covers/%Y/', null=True, blank=True)
    description      = models.TextField(max_length=2000, blank=True)
    annee_creation   = models.IntegerField(null=True, blank=True)
    nb_employes      = models.CharField(max_length=20, choices=[
        ('1-5',   '1 à 5 employés'),
        ('6-20',  '6 à 20'),
        ('21-50', '21 à 50'),
        ('51-200','51 à 200'),
        ('200+',  'Plus de 200'),
    ], blank=True)

    # Localisation
    pays             = models.CharField(max_length=100)
    region           = models.CharField(max_length=100, blank=True)
    ville            = models.CharField(max_length=100)
    adresse          = models.TextField(blank=True)
    latitude         = models.FloatField(null=True, blank=True)
    longitude        = models.FloatField(null=True, blank=True)
    code_postal      = models.CharField(max_length=20, blank=True)

    # Contact professionnel
    telephone        = models.CharField(max_length=30)
    telephone2       = models.CharField(max_length=30, blank=True)
    whatsapp         = models.CharField(max_length=30, blank=True)
    email_pro        = models.EmailField()
    site_web         = models.URLField(blank=True)

    # Capacités
    superficie_ha    = models.FloatField(null=True, blank=True,
        help_text="Surface exploitée en hectares (producteurs)")
    capacite_stockage_tonnes     = models.FloatField(null=True, blank=True)
    volume_annuel_tonnes         = models.FloatField(null=True, blank=True,
        help_text="Volume annuel traité/produit en tonnes")
    devises_acceptees = models.JSONField(default=list,
        help_text="['XAF', 'EUR', 'USD', 'GBP', 'XOF']")
    modes_paiement   = models.JSONField(default=list,
        help_text="['Virement', 'Orange Money', 'MTN MoMo', 'PayPal', 'LC']")
    langues_travail  = models.JSONField(default=list,
        help_text="['Français', 'Anglais', 'Haoussa', ...]")

    # Zones de vente / achat
    vend_localement          = models.BooleanField(default=True)
    vend_nationalement       = models.BooleanField(default=True)
    vend_internationalement  = models.BooleanField(default=False)
    zones_export             = models.JSONField(default=list,
        help_text="['Europe', 'Amérique du Nord', 'Asie', 'Afrique subsaharienne']")

    # Statut et vérification
    est_verifie      = models.BooleanField(default=False)
    est_premium      = models.BooleanField(default=False)
    plan_premium     = models.CharField(max_length=20, choices=[
        ('free',     'Gratuit'),
        ('silver',   'Silver'),
        ('gold',     'Gold'),
        ('platinum', 'Platinum'),
    ], default='free')
    plan_expiry      = models.DateField(null=True, blank=True)
    est_actif        = models.BooleanField(default=True)
    est_en_ligne     = models.BooleanField(default=True)
    profil_complet   = models.IntegerField(default=0,
        help_text="Pourcentage de complétion du profil 0-100")
    score_confiance  = models.FloatField(default=0.0,
        help_text="Score 0-100 basé sur avis, ancienneté, certifications")

    # Statistiques
    nb_vues          = models.IntegerField(default=0)
    nb_produits      = models.IntegerField(default=0)
    nb_commandes     = models.IntegerField(default=0)
    nb_avis          = models.IntegerField(default=0)
    note_moyenne     = models.FloatField(default=0.0)

    # Métadonnées
    date_inscription  = models.DateTimeField(auto_now_add=True)
    derniere_activite = models.DateTimeField(auto_now=True)
    slug              = models.SlugField(unique=True, max_length=200)

    class Meta:
        verbose_name = "Acteur agroalimentaire"
        verbose_name_plural = "Acteurs agroalimentaires"
        ordering = ['-score_confiance', '-date_inscription']
        indexes = [
            models.Index(fields=['pays', 'type_acteur']),
            models.Index(fields=['est_verifie', 'est_actif']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.nom_entreprise} ({self.get_type_acteur_display()}) — {self.pays}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.nom_entreprise}-{self.pays}")
            slug = base_slug
            n = 1
            while ActeurAgro.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('agro:profil', kwargs={'slug': self.slug})

    def calculer_profil_complet(self):
        """Calcule le pourcentage de complétion du profil."""
        champs = [
            self.logo, self.photo_couverture, self.description,
            self.telephone, self.email_pro, self.ville, self.pays,
            self.langues_travail, self.modes_paiement,
        ]
        remplis = sum(1 for c in champs if c)
        self.profil_complet = int((remplis / len(champs)) * 100)
        return self.profil_complet

    @property
    def est_vendeur(self):
        return self.type_acteur in [
            TypeActeur.PRODUCTEUR, TypeActeur.ELEVEUR,
            TypeActeur.TRANSFORMATEUR, TypeActeur.COOPERATIVE,
            TypeActeur.EXPORTATEUR, TypeActeur.GROSSISTE,
        ]

    @property
    def est_acheteur(self):
        return self.type_acteur in [
            TypeActeur.IMPORTATEUR, TypeActeur.GRANDE_SURFACE,
            TypeActeur.RESTAURATEUR, TypeActeur.INDUSTRIE,
            TypeActeur.GROSSISTE,
        ]

    @property
    def badge_plan(self):
        badges = {
            'free':     '',
            'silver':   '🥈',
            'gold':     '🥇',
            'platinum': '💎',
        }
        return badges.get(self.plan_premium, '')
