from django.db import models
from django.utils import timezone


class CertificationAgro(models.Model):
    """Certifications et labels qualité des acteurs agroalimentaires."""
    TYPE_CHOICES = [
        ('bio',         'Agriculture Biologique'),
        ('equitable',   'Commerce Équitable'),
        ('iso',         'ISO (22000, 9001, 14001...)'),
        ('globalgap',   'GlobalGAP'),
        ('haccp',       'HACCP'),
        ('halal',       'Halal'),
        ('kosher',      'Kasher'),
        ('rainforest',  'Rainforest Alliance'),
        ('ue_bio',      'Bio Européen (AB)'),
        ('usda',        'USDA Organic'),
        ('national',    'Norme nationale'),
        ('autre',       'Autre certification'),
    ]

    acteur             = models.ForeignKey('agro.ActeurAgro', on_delete=models.CASCADE,
                           related_name='certifications')
    type_certification = models.CharField(max_length=20, choices=TYPE_CHOICES)
    nom                = models.CharField(max_length=200)
    organisme          = models.CharField(max_length=200,
                           help_text="Organisme certificateur")
    numero             = models.CharField(max_length=100, blank=True)
    date_obtention     = models.DateField()
    date_expiration    = models.DateField(null=True, blank=True)
    document           = models.FileField(upload_to='agro/certifications/',
                           null=True, blank=True)
    est_verifie_admin  = models.BooleanField(default=False)
    est_valide         = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_obtention']
        verbose_name = "Certification agro"
        verbose_name_plural = "Certifications agro"

    def __str__(self):
        return f"{self.nom} — {self.acteur.nom_entreprise}"

    def est_expire(self):
        if self.date_expiration:
            return self.date_expiration < timezone.now().date()
        return False

    @property
    def icone(self):
        icones = {
            'bio':        '🌿',
            'equitable':  '🤝',
            'iso':        '🏭',
            'globalgap':  '🌍',
            'haccp':      '🔬',
            'halal':      '☪️',
            'kosher':     '✡️',
            'rainforest': '🌲',
            'ue_bio':     '🇪🇺',
            'usda':       '🇺🇸',
            'national':   '🏳️',
            'autre':      '📋',
        }
        return icones.get(self.type_certification, '📋')
