from django.db import models


class Conversation(models.Model):
    match = models.OneToOneField(
        'rencontres.Match',
        on_delete=models.CASCADE,
        related_name='conversation'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    dernier_message_at = models.DateTimeField(null=True, blank=True)
    est_archivee = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Conversation"
        ordering = ['-dernier_message_at']

    def get_derniers_messages(self, n=20):
        return self.messages.order_by('-date_envoi')[:n]

    def get_other_profil(self, profil):
        return self.match.get_other_profil(profil)

    def nb_non_lus(self, profil):
        return self.messages.filter(est_lu=False).exclude(expediteur=profil).count()

    def __str__(self):
        return f"Conv — {self.match}"


class Message(models.Model):
    TYPE_CHOICES = [
        ('texte', 'Texte'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('emoji', 'Emoji'),
    ]
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    expediteur = models.ForeignKey(
        'rencontres.ProfilRencontre',
        on_delete=models.CASCADE,
        related_name='messages_envoyes'
    )
    type_message = models.CharField(max_length=20, choices=TYPE_CHOICES, default='texte')
    contenu = models.TextField(blank=True)
    fichier = models.FileField(
        upload_to='rencontres/messages/%Y/%m/',
        null=True, blank=True
    )
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)
    date_lecture = models.DateTimeField(null=True, blank=True)
    est_supprime_expediteur = models.BooleanField(default=False)
    est_supprime_destinataire = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Message"
        ordering = ['date_envoi']

    def __str__(self):
        return f"{self.expediteur}: {self.contenu[:50]}"
