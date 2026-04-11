from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Classe(models.Model):
    NIVEAUX = [
        ('3eme', 'Troisième'),
        ('2nde', 'Seconde'),
        ('1ere_a', 'Première A'),
        ('1ere_c', 'Première C'),
        ('1ere_d', 'Première D'),
        ('tle_a', 'Terminale A'),
        ('tle_c', 'Terminale C'),
        ('tle_d', 'Terminale D'),
    ]
    EXAMENS = [
        ('bepc', 'BEPC'),
        ('probatoire', 'Probatoire'),
        ('baccalaureat', 'Baccalauréat'),
    ]
    nom = models.CharField(max_length=20, choices=NIVEAUX, unique=True)
    label = models.CharField(max_length=50)
    examen_fin_annee = models.CharField(max_length=20, choices=EXAMENS, blank=True)
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=7, default='#2E7D32')
    icone = models.CharField(max_length=50, default='calculator')
    ordre = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return self.label

    def get_examen_label(self):
        return dict(self.EXAMENS).get(self.examen_fin_annee, '')


class Chapitre(models.Model):
    CATEGORIES = [
        ('algebre', 'Algèbre'),
        ('geometrie', 'Géométrie'),
        ('analyse', 'Analyse'),
        ('statistiques', 'Statistiques & Probabilités'),
        ('arithmetique', 'Arithmétique'),
        ('trigonometrie', 'Trigonométrie'),
        ('logique', 'Logique & Ensembles'),
        ('complexes', 'Nombres Complexes'),
        ('suites', 'Suites & Séries'),
        ('matrices', 'Matrices & Déterminants'),
    ]
    DIFFICULTES = [
        (1, 'Facile'),
        (2, 'Moyen'),
        (3, 'Difficile'),
        (4, 'Très difficile'),
    ]
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='chapitres')
    titre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    numero = models.PositiveIntegerField()
    categorie = models.CharField(max_length=30, choices=CATEGORIES)
    difficulte = models.IntegerField(choices=DIFFICULTES, default=2)
    description = models.TextField(blank=True)
    objectifs = models.JSONField(default=list)
    prerequis = models.ManyToManyField('self', blank=True, symmetrical=False)
    duree_estimee = models.PositiveIntegerField(default=60)
    is_published = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['classe', 'numero']
        unique_together = ['classe', 'numero']

    def __str__(self):
        return f"{self.classe} - Ch.{self.numero} : {self.titre}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.classe.nom}-{self.numero}-{self.titre}")[:210]
            self.slug = base
        super().save(*args, **kwargs)

    @property
    def nb_lecons(self):
        return self.lecons.count()

    @property
    def nb_exercices(self):
        return self.exercices.count()


class Lecon(models.Model):
    TYPES = [
        ('definition', 'Définition & Théorie'),
        ('methode', 'Méthode & Technique'),
        ('exemple', 'Exemples résolus'),
        ('recapitulatif', 'Récapitulatif'),
    ]
    chapitre = models.ForeignKey(Chapitre, on_delete=models.CASCADE, related_name='lecons')
    titre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    ordre = models.PositiveIntegerField()
    type_lecon = models.CharField(max_length=20, choices=TYPES, default='definition')
    contenu = models.JSONField(default=dict)
    contenu_html = models.TextField(blank=True)
    duree_lecture = models.PositiveIntegerField(default=15)
    is_free = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chapitre', 'ordre']
        unique_together = ['chapitre', 'ordre']

    def __str__(self):
        return f"{self.chapitre.titre} - L{self.ordre}: {self.titre}"


class Exercice(models.Model):
    TYPES = [
        ('qcm', 'QCM'),
        ('vrai_faux', 'Vrai ou Faux'),
        ('calcul', 'Calcul dirigé'),
        ('probleme', 'Problème ouvert'),
        ('demonstration', 'Démonstration'),
        ('application', 'Application directe'),
        ('synthese', 'Synthèse'),
    ]
    NIVEAUX = [
        ('decouverte', '⭐ Découverte'),
        ('entrainement', '⭐⭐ Entraînement'),
        ('approfondissement', '⭐⭐⭐ Approfondissement'),
        ('examen', '⭐⭐⭐⭐ Niveau examen'),
    ]
    chapitre = models.ForeignKey(Chapitre, on_delete=models.CASCADE, related_name='exercices')
    lecon = models.ForeignKey(Lecon, on_delete=models.SET_NULL, null=True, blank=True, related_name='exercices')
    titre = models.CharField(max_length=200)
    numero = models.PositiveIntegerField()
    type_exercice = models.CharField(max_length=20, choices=TYPES)
    niveau = models.CharField(max_length=20, choices=NIVEAUX, default='entrainement')
    enonce = models.JSONField(default=dict)
    correction = models.JSONField(default=dict)
    options_qcm = models.JSONField(default=list)
    bareme = models.PositiveIntegerField(default=5)
    duree_recommandee = models.PositiveIntegerField(default=20)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chapitre', 'numero']

    def __str__(self):
        return f"Ex.{self.numero} — {self.titre} ({self.get_niveau_display()})"


class EpreuveExamen(models.Model):
    TYPES_EXAM = [
        ('bepc', 'BEPC'),
        ('probatoire', 'Probatoire'),
        ('baccalaureat', 'Baccalauréat'),
        ('entrainement', 'Entraînement'),
    ]
    SERIES = [
        ('toutes', 'Toutes séries'),
        ('A', 'Série A'),
        ('C', 'Série C'),
        ('D', 'Série D'),
    ]
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='epreuves')
    type_examen = models.CharField(max_length=20, choices=TYPES_EXAM)
    serie = models.CharField(max_length=10, choices=SERIES, default='toutes')
    annee = models.PositiveIntegerField(null=True, blank=True)
    region = models.CharField(max_length=50, blank=True)
    duree = models.PositiveIntegerField(default=180)
    bareme_total = models.PositiveIntegerField(default=20)
    contenu = models.JSONField(default=dict)
    correction_complete = models.JSONField(default=dict)
    is_premium = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-annee', 'classe']

    def __str__(self):
        return f"{self.titre} — {self.classe}"


class ProfilEleve(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profil_eleve')
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)
    etablissement = models.CharField(max_length=200, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='enfants')
    points_total = models.PositiveIntegerField(default=0)
    streak_jours = models.PositiveIntegerField(default=0)
    derniere_connexion_app = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Élève : {self.user.get_full_name() or self.user.username}"

    @property
    def niveau_badge(self):
        if self.points_total < 100: return 'Débutant'
        elif self.points_total < 500: return 'Apprenti'
        elif self.points_total < 1000: return 'Intermédiaire'
        elif self.points_total < 2000: return 'Avancé'
        else: return 'Expert'


class ProgressionLecon(models.Model):
    eleve = models.ForeignKey(ProfilEleve, on_delete=models.CASCADE, related_name='progressions')
    lecon = models.ForeignKey(Lecon, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    temps_passe = models.PositiveIntegerField(default=0)
    nb_consultations = models.PositiveIntegerField(default=0)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_completion = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['eleve', 'lecon']


class ResultatExercice(models.Model):
    eleve = models.ForeignKey(ProfilEleve, on_delete=models.CASCADE, related_name='resultats')
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE)
    tentative = models.PositiveIntegerField(default=1)
    score = models.FloatField(default=0)
    points_obtenus = models.FloatField(default=0)
    reponses_eleve = models.JSONField(default=dict)
    temps_passe = models.PositiveIntegerField(default=0)
    correction_consultee = models.BooleanField(default=False)
    date_tentative = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_tentative']


class ResultatEpreuve(models.Model):
    eleve = models.ForeignKey(ProfilEleve, on_delete=models.CASCADE, related_name='resultats_epreuves')
    epreuve = models.ForeignKey(EpreuveExamen, on_delete=models.CASCADE)
    note = models.FloatField()
    temps_passe = models.PositiveIntegerField()
    reponses = models.JSONField(default=dict)
    analyse = models.JSONField(default=dict)
    date_passage = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_passage']


class Badge(models.Model):
    TYPES = [
        ('completion', 'Complétion chapitre'),
        ('score', 'Score parfait'),
        ('streak', 'Régularité'),
        ('rapidite', 'Rapidité'),
        ('examen', 'Réussite examen'),
    ]
    nom = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    type_badge = models.CharField(max_length=20, choices=TYPES)
    icone = models.CharField(max_length=100)
    condition_points = models.PositiveIntegerField(default=0)
    eleves = models.ManyToManyField(ProfilEleve, blank=True, related_name='badges')

    def __str__(self):
        return self.nom
