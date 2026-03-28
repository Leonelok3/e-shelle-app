"""
payments/models.py — Module Paiements E-Shelle
Transactions Mobile Money, historique, remboursements.
"""
from django.db import models
from django.conf import settings
import uuid


class Transaction(models.Model):
    METHODES = [
        ("mtn_momo",   "MTN Mobile Money"),
        ("airtel",     "Airtel Money"),
        ("orange",     "Orange Money"),
        ("carte",      "Carte bancaire"),
        ("virement",   "Virement bancaire"),
        ("gratuit",    "Gratuit (coupon)"),
    ]
    STATUTS = [
        ("initie",     "Initié"),
        ("en_attente", "En attente de confirmation"),
        ("succes",     "Succès"),
        ("echec",      "Échec"),
        ("expire",     "Expiré"),
        ("rembourse",  "Remboursé"),
    ]
    TYPES = [
        ("achat_cours",        "Achat formation"),
        ("achat_produit",      "Achat produit boutique"),
        ("abonnement",         "Abonnement Pro/Enterprise"),
        ("service",            "Paiement service"),
        ("remboursement",      "Remboursement"),
        ("premium_marketplac", "Pack Premium marketplace"),
        ("boost_annonce",      "Boost annonce/bien/véhicule"),
    ]

    reference    = models.CharField(max_length=40, unique=True, blank=True)
    utilisateur  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                      related_name="transactions")
    type_tx      = models.CharField(max_length=20, choices=TYPES)
    methode      = models.CharField(max_length=20, choices=METHODES, default="mtn_momo")
    montant      = models.DecimalField(max_digits=12, decimal_places=2)
    devise       = models.CharField(max_length=5, default="XAF")
    telephone    = models.CharField(max_length=25, blank=True,
                                     help_text="Numéro Mobile Money")
    statut       = models.CharField(max_length=20, choices=STATUTS, default="initie")
    # Références externes (API paiement)
    ref_operateur = models.CharField(max_length=200, blank=True,
                                      help_text="Référence de l'opérateur MTN/Airtel")
    ref_interne  = models.CharField(max_length=200, blank=True)
    # Objet payé
    commande     = models.ForeignKey("boutique.Commande", on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name="transactions")
    formation    = models.ForeignKey("formations.Formation", on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name="transactions")
    metadata     = models.JSONField(default=dict, blank=True)
    erreur       = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Transaction"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"TX-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} — {self.utilisateur.username} — {self.montant} {self.devise} ({self.statut})"


class Coupon(models.Model):
    """Codes promo et réductions."""
    TYPES = [
        ("pourcent",  "Pourcentage de réduction"),
        ("fixe",      "Montant fixe"),
        ("gratuit",   "Accès gratuit"),
    ]

    code         = models.CharField(max_length=50, unique=True)
    type_coupon  = models.CharField(max_length=10, choices=TYPES, default="pourcent")
    valeur       = models.DecimalField(max_digits=8, decimal_places=2, default=0,
                                        help_text="Valeur (% ou FCFA selon le type)")
    max_utilisations = models.PositiveIntegerField(default=0,
                                                     help_text="0 = illimité")
    nb_utilisations  = models.PositiveIntegerField(default=0)
    date_debut   = models.DateTimeField(null=True, blank=True)
    date_fin     = models.DateTimeField(null=True, blank=True)
    actif        = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Coupon"

    def __str__(self):
        return f"{self.code} ({self.valeur}{'%' if self.type_coupon == 'pourcent' else ' FCFA'})"

    @property
    def est_valide(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.actif:
            return False
        if self.date_debut and now < self.date_debut:
            return False
        if self.date_fin and now > self.date_fin:
            return False
        if self.max_utilisations > 0 and self.nb_utilisations >= self.max_utilisations:
            return False
        return True
