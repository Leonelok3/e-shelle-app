from django.db import models


class Like(models.Model):
    TYPE_CHOICES = [
        ('like', 'Like'),
        ('super_like', 'Super Like'),
    ]
    envoyeur = models.ForeignKey(
        'rencontres.ProfilRencontre',
        on_delete=models.CASCADE,
        related_name='likes_envoyes'
    )
    recepteur = models.ForeignKey(
        'rencontres.ProfilRencontre',
        on_delete=models.CASCADE,
        related_name='likes_recus'
    )
    type_like = models.CharField(max_length=20, choices=TYPE_CHOICES, default='like')
    date_like = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Like"
        unique_together = ('envoyeur', 'recepteur')

    def __str__(self):
        return f"{self.envoyeur} → {self.recepteur} ({self.type_like})"


class Match(models.Model):
    profil_1 = models.ForeignKey(
        'rencontres.ProfilRencontre',
        on_delete=models.CASCADE,
        related_name='matchs_1'
    )
    profil_2 = models.ForeignKey(
        'rencontres.ProfilRencontre',
        on_delete=models.CASCADE,
        related_name='matchs_2'
    )
    date_match = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)
    score_compatibilite = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Match"
        unique_together = ('profil_1', 'profil_2')

    def get_other_profil(self, profil):
        return self.profil_2 if self.profil_1 == profil else self.profil_1

    def __str__(self):
        return f"Match: {self.profil_1} ❤️ {self.profil_2}"


class Blocage(models.Model):
    bloqueur = models.ForeignKey(
        'rencontres.ProfilRencontre',
        on_delete=models.CASCADE,
        related_name='blocages_effectues'
    )
    bloque = models.ForeignKey(
        'rencontres.ProfilRencontre',
        on_delete=models.CASCADE,
        related_name='blocages_subis'
    )
    raison = models.CharField(max_length=100, blank=True)
    date_blocage = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Blocage"
        unique_together = ('bloqueur', 'bloque')

    def __str__(self):
        return f"{self.bloqueur} bloque {self.bloque}"
