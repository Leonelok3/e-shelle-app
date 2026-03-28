from django.db import models
from .produit import UniteMesure


class OffreCommerciale(models.Model):
    """Offre promotionnelle publiée par un acteur (vente ou achat)."""
    TYPE_CHOICES = [
        ('vente',       'Offre de vente'),
        ('achat',       "Demande d'achat"),
        ('echange',     'Échange / Troc'),
        ('partenariat', 'Recherche partenariat'),
    ]
    DEVISE_CHOICES = [
        ('XAF', 'FCFA CFA'), ('XOF', 'FCFA Ouest'),
        ('EUR', 'Euro'), ('USD', 'Dollar USD'),
        ('GBP', 'Livre Sterling'), ('NGN', 'Naira'),
    ]

    acteur       = models.ForeignKey('agro.ActeurAgro', on_delete=models.CASCADE,
                     related_name='offres')
    produit      = models.ForeignKey('agro.ProduitAgro', on_delete=models.SET_NULL,
                     null=True, blank=True, related_name='offres')
    type_offre   = models.CharField(max_length=20, choices=TYPE_CHOICES)
    titre        = models.CharField(max_length=200)
    description  = models.TextField()
    quantite     = models.FloatField()
    unite_mesure = models.CharField(max_length=10, choices=UniteMesure.choices)
    prix_propose = models.DecimalField(max_digits=15, decimal_places=2,
                     null=True, blank=True)
    devise       = models.CharField(max_length=5, default='XAF', choices=DEVISE_CHOICES)
    date_validite    = models.DateField()
    lieu_livraison   = models.CharField(max_length=200, blank=True)
    conditions       = models.TextField(blank=True)
    est_urgente      = models.BooleanField(default=False)
    est_active       = models.BooleanField(default=True)
    nb_vues          = models.IntegerField(default=0)
    nb_contacts      = models.IntegerField(default=0)
    date_publication = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-est_urgente', '-date_publication']
        verbose_name = "Offre commerciale"
        verbose_name_plural = "Offres commerciales"

    def __str__(self):
        return f"{self.get_type_offre_display()} — {self.titre}"


class AppelOffre(models.Model):
    """Appel d'offre lancé par un acheteur."""
    DEVISE_CHOICES = [
        ('XAF', 'FCFA CFA'), ('EUR', 'Euro'), ('USD', 'Dollar USD'),
    ]

    acheteur     = models.ForeignKey('agro.ActeurAgro', on_delete=models.CASCADE,
                     related_name='appels_offre')
    titre        = models.CharField(max_length=200)
    description  = models.TextField()
    categorie    = models.ForeignKey('agro.CategorieAgro', on_delete=models.SET_NULL,
                     null=True, related_name='appels_offre')
    quantite_min = models.FloatField()
    quantite_max = models.FloatField(null=True, blank=True)
    unite_mesure = models.CharField(max_length=10, choices=UniteMesure.choices)
    budget_max   = models.DecimalField(max_digits=15, decimal_places=2,
                     null=True, blank=True)
    devise       = models.CharField(max_length=5, default='USD', choices=DEVISE_CHOICES)
    pays_origine_requis      = models.JSONField(default=list)
    certifications_requises  = models.JSONField(default=list)
    date_limite_soumission   = models.DateTimeField()
    date_livraison_souhaitee = models.DateField(null=True, blank=True)
    incoterm_souhaite        = models.CharField(max_length=10, blank=True)
    est_publie   = models.BooleanField(default=True)
    est_urgent   = models.BooleanField(default=False)
    nb_reponses  = models.IntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-est_urgent', '-date_creation']
        verbose_name = "Appel d'offre"
        verbose_name_plural = "Appels d'offre"

    def __str__(self):
        return f"AO — {self.titre} ({self.acheteur.nom_entreprise})"


class ReponseAppelOffre(models.Model):
    """Réponse d'un fournisseur à un appel d'offre."""
    STATUT_CHOICES = [
        ('soumise',       'Soumise'),
        ('en_evaluation', 'En évaluation'),
        ('acceptee',      'Acceptée'),
        ('refusee',       'Refusée'),
    ]
    INCOTERM_CHOICES = [
        ('EXW', 'EXW'), ('FOB', 'FOB'), ('CIF', 'CIF'),
        ('DAP', 'DAP'), ('DDP', 'DDP'), ('CFR', 'CFR'),
    ]

    appel_offre         = models.ForeignKey(AppelOffre, on_delete=models.CASCADE,
                            related_name='reponses')
    fournisseur         = models.ForeignKey('agro.ActeurAgro', on_delete=models.CASCADE,
                            related_name='reponses_ao')
    prix_unitaire       = models.DecimalField(max_digits=15, decimal_places=2)
    devise              = models.CharField(max_length=5)
    quantite_disponible = models.FloatField()
    delai_jours         = models.IntegerField()
    incoterm            = models.CharField(max_length=10, choices=INCOTERM_CHOICES)
    conditions          = models.TextField()
    documents_joints    = models.JSONField(default=list)
    statut              = models.CharField(max_length=20, choices=STATUT_CHOICES,
                            default='soumise')
    date_soumission     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Réponse appel d'offre"
        verbose_name_plural = "Réponses appels d'offre"
        ordering = ['-date_soumission']

    def __str__(self):
        return f"Réponse de {self.fournisseur.nom_entreprise} à {self.appel_offre.titre}"
