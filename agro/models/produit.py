import uuid
from django.db import models
from django.utils.text import slugify
from .acteur import ActeurAgro


class CategorieAgro(models.Model):
    """Arborescence catégories agroalimentaires (2 niveaux max)."""
    nom         = models.CharField(max_length=100)
    slug        = models.SlugField(max_length=120, unique=True)
    parent      = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='sous_categories'
    )
    icone       = models.CharField(max_length=10, blank=True,
                    help_text="Emoji ou classe icon")
    image       = models.ImageField(upload_to='agro/categories/', null=True, blank=True)
    description = models.TextField(blank=True)
    ordre       = models.IntegerField(default=0)
    est_active  = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Catégorie agro"
        verbose_name_plural = "Catégories agro"

    def __str__(self):
        if self.parent:
            return f"{self.parent.nom} > {self.nom}"
        return f"{self.icone} {self.nom}".strip()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('agro:categorie', kwargs={'slug': self.slug})

    @property
    def nb_produits(self):
        return self.produits.filter(statut='publie').count()


class UniteMesure(models.TextChoices):
    KG          = 'kg',    'Kilogramme (kg)'
    TONNE       = 't',     'Tonne (t)'
    LITRE       = 'l',     'Litre (L)'
    PIECE       = 'pce',   'Pièce / Unité'
    CAISSE      = 'caisse','Caisse'
    SAC         = 'sac',   'Sac'
    TETE        = 'tete',  'Tête (animaux vivants)'
    HECTARE     = 'ha',    'Hectare'
    CONTAINER   = 'cnt',   'Conteneur (20 pieds)'
    CONTAINER40 = 'cnt40', 'Conteneur (40 pieds)'
    PALETTE     = 'pal',   'Palette'
    BOTTE       = 'botte', 'Botte'


class ProduitAgro(models.Model):
    """Fiche produit agroalimentaire complète."""

    STATUT_CHOICES = [
        ('brouillon',   'Brouillon'),
        ('en_attente',  'En attente de validation'),
        ('publie',      'Publié'),
        ('epuise',      'Épuisé temporairement'),
        ('suspendu',    'Suspendu'),
        ('archive',     'Archivé'),
    ]

    DISPONIBILITE_CHOICES = [
        ('en_stock',     'En stock immédiat'),
        ('sur_commande', 'Sur commande (délai à préciser)'),
        ('saisonnier',   'Saisonnier'),
        ('pre_commande', 'Pré-commande (récolte future)'),
    ]

    DEVISE_CHOICES = [
        ('XAF', 'FCFA CFA'),
        ('XOF', 'FCFA Ouest'),
        ('EUR', 'Euro'),
        ('USD', 'Dollar USD'),
        ('GBP', 'Livre Sterling'),
        ('NGN', 'Naira'),
        ('GHS', 'Cedi Ghana'),
        ('MAD', 'Dirham Maroc'),
    ]

    acteur    = models.ForeignKey(ActeurAgro, on_delete=models.CASCADE,
                  related_name='produits')
    categorie = models.ForeignKey(CategorieAgro, on_delete=models.PROTECT,
                  related_name='produits')

    # Identification
    nom         = models.CharField(max_length=200)
    nom_local   = models.CharField(max_length=200, blank=True,
                    help_text="Nom en langue locale (ex: Ndolé, Egusi, Foutou...)")
    slug        = models.SlugField(max_length=250, unique=True)
    reference   = models.CharField(max_length=50, unique=True, blank=True,
                    help_text="Référence interne auto-générée")
    code_hs     = models.CharField(max_length=20, blank=True,
                    help_text="Code SH douanier pour l'export international")

    # Description
    description          = models.TextField(max_length=3000)
    caracteristiques     = models.JSONField(default=dict,
        help_text="{'variete': 'Valencia', 'calibre': '80/100', 'humidite': '14%'}")
    origine_geographique = models.CharField(max_length=200, blank=True,
        help_text="Ex: Région de l'Ouest Cameroun, Vallée du Ntem")

    # Pricing
    prix_unitaire   = models.DecimalField(max_digits=15, decimal_places=2,
                        help_text="Prix de base par unité")
    devise          = models.CharField(max_length=5, default='XAF',
                        choices=DEVISE_CHOICES)
    prix_negociable = models.BooleanField(default=True)
    prix_degressif  = models.JSONField(default=list,
        help_text="[{'qte_min': 1000, 'prix': 450}, {'qte_min': 5000, 'prix': 400}]")

    # Quantités
    unite_mesure          = models.CharField(max_length=10, choices=UniteMesure.choices)
    quantite_stock        = models.FloatField(default=0)
    quantite_min_commande = models.FloatField(default=1,
        help_text="Quantité minimale de commande (MOQ)")
    quantite_max_commande = models.FloatField(null=True, blank=True)
    conditionnement       = models.CharField(max_length=200, blank=True,
        help_text="Ex: Sacs de 50kg, Cartons de 12kg, Fûts de 200L")

    # Disponibilité et production
    disponibilite                = models.CharField(max_length=20,
                                     choices=DISPONIBILITE_CHOICES, default='en_stock')
    delai_livraison_jours        = models.IntegerField(default=7)
    saison_disponible            = models.CharField(max_length=200, blank=True,
        help_text="Ex: Octobre à Février, Disponible toute l'année")
    production_annuelle_tonnes   = models.FloatField(null=True, blank=True)

    # Qualité et certifications
    normes_qualite = models.JSONField(default=list,
        help_text="['ISO 22000', 'GlobalGAP', 'Bio AB', 'Rainforest Alliance', 'Fairtrade']")
    est_bio        = models.BooleanField(default=False)
    est_equitable  = models.BooleanField(default=False)
    taux_humidite  = models.FloatField(null=True, blank=True)
    granulometrie  = models.CharField(max_length=100, blank=True)
    autres_specs   = models.TextField(blank=True)

    # Logistique export
    incoterms_disponibles        = models.JSONField(default=list,
        help_text="['EXW', 'FOB', 'CIF', 'DAP', 'DDP']")
    port_embarquement            = models.CharField(max_length=100, blank=True,
        help_text="Ex: Port de Douala, Port d'Abidjan")
    peut_exporter                = models.BooleanField(default=False)
    pays_export_autorises        = models.JSONField(default=list,
        help_text="Vide = tous les pays")
    documents_export_disponibles = models.JSONField(default=list,
        help_text="['Phytosanitaire', 'Certificat origine', 'Analyse labo', 'CITES']")

    # Médias
    image_principale = models.ImageField(upload_to='agro/produits/%Y/%m/',
                         null=True, blank=True)
    video_url        = models.URLField(blank=True,
        help_text="Lien YouTube ou Vimeo de présentation")

    # Statut et stats
    statut           = models.CharField(max_length=20,
                         choices=STATUT_CHOICES, default='en_attente')
    est_mis_en_avant = models.BooleanField(default=False)
    nb_vues          = models.IntegerField(default=0)
    nb_demandes      = models.IntegerField(default=0)
    nb_favoris       = models.IntegerField(default=0)
    note_moyenne     = models.FloatField(default=0.0)

    # Favoris (relation ManyToMany vers les ActeurAgro)
    favoris          = models.ManyToManyField(
        ActeurAgro, blank=True, related_name='produits_favoris'
    )

    # Métadonnées SEO
    meta_titre       = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    tags             = models.JSONField(default=list)

    date_creation    = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit agroalimentaire"
        verbose_name_plural = "Produits agroalimentaires"
        ordering = ['-est_mis_en_avant', '-nb_vues']
        indexes = [
            models.Index(fields=['categorie', 'statut']),
            models.Index(fields=['acteur', 'statut']),
            models.Index(fields=['peut_exporter', 'statut']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.nom} — {self.acteur.nom_entreprise}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"AGRO-{uuid.uuid4().hex[:8].upper()}"
        if not self.slug:
            base_slug = slugify(f"{self.nom}-{self.acteur.pays}")
            slug = base_slug
            n = 1
            while ProduitAgro.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        if not self.meta_titre:
            self.meta_titre = f"{self.nom} — {self.acteur.pays} | E-Shelle Agro"
        if not self.meta_description:
            self.meta_description = self.description[:157] + "..." if len(self.description) > 160 else self.description
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('agro:produit', kwargs={'slug': self.slug})

    @property
    def est_disponible(self):
        return self.statut == 'publie' and self.disponibilite in ['en_stock', 'sur_commande']

    @property
    def badges(self):
        badges = []
        if self.est_bio:
            badges.append({'label': 'Bio', 'icon': '🌿', 'classe': 'badge-bio'})
        if self.est_equitable:
            badges.append({'label': 'Équitable', 'icon': '🤝', 'classe': 'badge-equitable'})
        if self.peut_exporter:
            badges.append({'label': 'Export', 'icon': '🚢', 'classe': 'badge-export'})
        return badges


class PhotoProduit(models.Model):
    produit  = models.ForeignKey(ProduitAgro, on_delete=models.CASCADE,
                 related_name='photos')
    image    = models.ImageField(upload_to='agro/produits/%Y/%m/')
    legende  = models.CharField(max_length=200, blank=True)
    est_principale = models.BooleanField(default=False)
    ordre    = models.IntegerField(default=0)

    class Meta:
        ordering = ['ordre']
        verbose_name = "Photo produit"
        verbose_name_plural = "Photos produit"

    def __str__(self):
        return f"Photo de {self.produit.nom} #{self.ordre}"


class ModerationProduit(models.Model):
    """Workflow de validation avant publication."""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve',   'Approuvé'),
        ('rejete',     'Rejeté'),
    ]
    produit         = models.OneToOneField(ProduitAgro, on_delete=models.CASCADE,
                        related_name='moderation')
    moderateur      = models.ForeignKey(
        'accounts.CustomUser', null=True, blank=True, on_delete=models.SET_NULL
    )
    statut          = models.CharField(max_length=20, choices=STATUT_CHOICES,
                        default='en_attente')
    motif_rejet     = models.TextField(blank=True)
    date_moderation = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Modération produit"

    def __str__(self):
        return f"Modération: {self.produit.nom} ({self.statut})"
