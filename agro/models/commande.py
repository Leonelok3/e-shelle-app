import uuid
from django.db import models
from .produit import UniteMesure


class DemandeDevis(models.Model):
    """Demande de devis d'un acheteur vers un vendeur."""
    STATUT_CHOICES = [
        ('en_attente',   'En attente'),
        ('vue',          'Vue par le vendeur'),
        ('devis_envoye', 'Devis envoyé'),
        ('negocie',      'En négociation'),
        ('accepte',      'Accepté'),
        ('refuse',       'Refusé'),
        ('expire',       'Expiré'),
    ]
    INCOTERM_CHOICES = [
        ('', '— Non précisé —'),
        ('EXW', 'EXW'), ('FOB', 'FOB'), ('CIF', 'CIF'),
        ('DAP', 'DAP'), ('DDP', 'DDP'), ('CFR', 'CFR'),
    ]

    acheteur          = models.ForeignKey('agro.ActeurAgro', on_delete=models.CASCADE,
                          related_name='devis_envoyes')
    vendeur           = models.ForeignKey('agro.ActeurAgro', on_delete=models.CASCADE,
                          related_name='devis_recus')
    produit           = models.ForeignKey('agro.ProduitAgro', on_delete=models.SET_NULL,
                          null=True, blank=True)
    quantite          = models.FloatField()
    unite_mesure      = models.CharField(max_length=10, choices=UniteMesure.choices)
    destination       = models.CharField(max_length=200)
    incoterm_souhaite = models.CharField(max_length=10, blank=True,
                          choices=INCOTERM_CHOICES)
    message           = models.TextField()
    fichiers_joints   = models.JSONField(default=list)
    statut            = models.CharField(max_length=20, choices=STATUT_CHOICES,
                          default='en_attente')

    # Réponse du vendeur
    prix_propose         = models.DecimalField(max_digits=15, decimal_places=2,
                             null=True, blank=True)
    devise_propose       = models.CharField(max_length=5, null=True, blank=True)
    conditions_proposees = models.TextField(blank=True)
    date_validite_devis  = models.DateField(null=True, blank=True)

    reference        = models.CharField(max_length=50, unique=True, blank=True)
    date_creation    = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Demande de devis"
        verbose_name_plural = "Demandes de devis"

    def __str__(self):
        return f"{self.reference} — {self.acheteur.nom_entreprise} → {self.vendeur.nom_entreprise}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"DV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class CommandeAgro(models.Model):
    """Commande confirmée après acceptation du devis."""
    STATUT_CHOICES = [
        ('confirmee',      'Confirmée'),
        ('en_preparation', 'En préparation'),
        ('prete',          'Prête à expédier'),
        ('expedie',        'Expédiée'),
        ('en_transit',     'En transit'),
        ('livree',         'Livrée'),
        ('litige',         'Litige'),
        ('annulee',        'Annulée'),
        ('remboursee',     'Remboursée'),
    ]
    PAIEMENT_STATUT = [
        ('en_attente', 'En attente'),
        ('partiel',    'Partiel'),
        ('complete',   'Complet'),
        ('rembourse',  'Remboursé'),
    ]

    devis           = models.OneToOneField(DemandeDevis, on_delete=models.PROTECT,
                        related_name='commande')
    acheteur        = models.ForeignKey('agro.ActeurAgro', on_delete=models.PROTECT,
                        related_name='commandes_passees')
    vendeur         = models.ForeignKey('agro.ActeurAgro', on_delete=models.PROTECT,
                        related_name='commandes_recues')
    numero_commande = models.CharField(max_length=50, unique=True, blank=True)
    montant_total   = models.DecimalField(max_digits=15, decimal_places=2)
    devise          = models.CharField(max_length=5)
    statut          = models.CharField(max_length=20, choices=STATUT_CHOICES,
                        default='confirmee')

    # Logistique
    incoterm              = models.CharField(max_length=10)
    port_depart           = models.CharField(max_length=200, blank=True)
    port_arrivee          = models.CharField(max_length=200, blank=True)
    numero_connaissement  = models.CharField(max_length=100, blank=True)
    transporteur          = models.CharField(max_length=100, blank=True)
    date_expedition         = models.DateField(null=True, blank=True)
    date_livraison_prevue   = models.DateField(null=True, blank=True)
    date_livraison_reelle   = models.DateField(null=True, blank=True)

    # Paiement (lié au payments/ existant)
    paiement_transaction    = models.ForeignKey(
        'payments.Transaction', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='commandes_agro'
    )
    paiement_statut         = models.CharField(max_length=20, choices=PAIEMENT_STATUT,
                                default='en_attente')

    # Documents
    documents               = models.JSONField(default=list,
        help_text="URLs des documents : facture, BL, phytosanitaire, certificat...")

    # Notes
    notes_vendeur           = models.TextField(blank=True)
    notes_acheteur          = models.TextField(blank=True)
    notes_internes          = models.TextField(blank=True)

    date_creation    = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Commande agro"
        verbose_name_plural = "Commandes agro"

    def __str__(self):
        return f"{self.numero_commande} — {self.acheteur.nom_entreprise}"

    def save(self, *args, **kwargs):
        if not self.numero_commande:
            self.numero_commande = f"CMD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('agro:detail_commande', kwargs={'numero': self.numero_commande})
