from django.db import models


class ZoneLivraison(models.Model):
    """Zones de livraison gérées par un acteur."""
    acteur         = models.ForeignKey('agro.ActeurAgro', on_delete=models.CASCADE,
                       related_name='zones_livraison')
    nom            = models.CharField(max_length=200)
    pays           = models.CharField(max_length=100)
    region         = models.CharField(max_length=100, blank=True)
    delai_min_jours = models.IntegerField(default=1)
    delai_max_jours = models.IntegerField(default=30)
    cout_par_tonne  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    devise          = models.CharField(max_length=5, default='XAF')
    incoterms       = models.JSONField(default=list)
    notes           = models.TextField(blank=True)
    est_active      = models.BooleanField(default=True)

    class Meta:
        ordering = ['pays', 'nom']
        verbose_name = "Zone de livraison"
        verbose_name_plural = "Zones de livraison"

    def __str__(self):
        return f"{self.nom} ({self.pays}) — {self.acteur.nom_entreprise}"
