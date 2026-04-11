from django.db import models


class AvisActeur(models.Model):
    """Évaluation d'un acteur par un partenaire commercial."""
    NOTE_CHOICES = [(i, str(i)) for i in range(1, 6)]

    evaluateur           = models.ForeignKey('agro.ActeurAgro', on_delete=models.CASCADE,
                             related_name='avis_donnes')
    evalue               = models.ForeignKey('agro.ActeurAgro', on_delete=models.CASCADE,
                             related_name='avis_recus')
    commande             = models.ForeignKey('agro.CommandeAgro', on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='avis')

    # Notes détaillées (1-5)
    note_globale          = models.IntegerField(choices=NOTE_CHOICES)
    note_qualite_produit  = models.IntegerField(choices=NOTE_CHOICES)
    note_communication    = models.IntegerField(choices=NOTE_CHOICES)
    note_delais           = models.IntegerField(choices=NOTE_CHOICES)
    note_conditionnement  = models.IntegerField(choices=NOTE_CHOICES)

    commentaire     = models.TextField(max_length=2000)
    reponse_vendeur = models.TextField(blank=True,
                        help_text="Réponse publique du vendeur à l'avis")
    est_publie      = models.BooleanField(default=True)
    est_verifie     = models.BooleanField(default=False,
                        help_text="Avis lié à une vraie commande vérifiée")
    date_avis       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('evaluateur', 'evalue', 'commande')
        ordering = ['-date_avis']
        verbose_name = "Avis acteur"
        verbose_name_plural = "Avis acteurs"

    def __str__(self):
        return f"Avis {self.note_globale}/5 — {self.evaluateur.nom_entreprise} → {self.evalue.nom_entreprise}"

    @property
    def note_moyenne_details(self):
        return (
            self.note_qualite_produit +
            self.note_communication +
            self.note_delais +
            self.note_conditionnement
        ) / 4

    def etoiles(self):
        return '★' * self.note_globale + '☆' * (5 - self.note_globale)
