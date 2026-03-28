from django.db import models


class Signalement(models.Model):
    RAISON_CHOICES = [
        ('faux_profil', 'Faux profil / Usurpation'),
        ('harcelement', 'Harcèlement'),
        ('contenu_inapproprie', 'Contenu inapproprié'),
        ('spam', 'Spam'),
        ('arnaque', "Tentative d'arnaque"),
        ('autre', 'Autre'),
    ]
    ACTION_CHOICES = [
        ('', 'En attente'),
        ('avertissement', 'Avertissement envoyé'),
        ('suspension_temp', 'Suspension temporaire'),
        ('suspension_def', 'Suspension définitive'),
        ('ignore', 'Signalement ignoré'),
    ]

    signaleur = models.ForeignKey(
        'rencontres.ProfilRencontre',
        on_delete=models.CASCADE,
        related_name='signalements_effectues'
    )
    signale = models.ForeignKey(
        'rencontres.ProfilRencontre',
        on_delete=models.CASCADE,
        related_name='signalements_recus'
    )
    raison = models.CharField(max_length=50, choices=RAISON_CHOICES)
    description = models.TextField(blank=True)
    date_signalement = models.DateTimeField(auto_now_add=True)
    est_traite = models.BooleanField(default=False)
    action_prise = models.CharField(
        max_length=100, blank=True,
        choices=ACTION_CHOICES,
        default=''
    )
    traite_par = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='signalements_traites'
    )
    date_traitement = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"
        ordering = ['-date_signalement']
        unique_together = ('signaleur', 'signale', 'raison')

    def __str__(self):
        return f"{self.signaleur} signale {self.signale} ({self.raison})"
