"""
formations/models.py — Module Formation en ligne E-Shelle
Cours, chapitres, leçons, quiz, progression, certificats.
"""
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Categorie(models.Model):
    nom    = models.CharField(max_length=100)
    slug   = models.SlugField(max_length=120, unique=True, blank=True)
    icone  = models.CharField(max_length=10, default="📚", help_text="Emoji")
    ordre  = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "Catégorie"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Formation(models.Model):
    NIVEAUX = [
        ("debutant",       "Débutant"),
        ("intermediaire",  "Intermédiaire"),
        ("avance",         "Avancé"),
        ("tous_niveaux",   "Tous niveaux"),
    ]
    LANGUES = [("fr", "Français"), ("en", "Anglais"), ("bi", "Bilingue")]

    titre             = models.CharField(max_length=200)
    slug              = models.SlugField(max_length=220, unique=True, blank=True)
    description       = models.TextField()
    description_courte = models.CharField(max_length=300, blank=True)
    thumbnail         = models.ImageField(upload_to="formations/thumbnails/", null=True, blank=True)
    video_intro       = models.URLField(blank=True)
    categorie         = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="formations")
    formateur         = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="formations_creees", null=True, blank=True
    )
    niveau            = models.CharField(max_length=20, choices=NIVEAUX, default="debutant")
    langue            = models.CharField(max_length=5, choices=LANGUES, default="fr")
    prix              = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                             help_text="Prix en FCFA (0 = gratuit)")
    prix_barre        = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_published      = models.BooleanField(default=False)
    is_featured       = models.BooleanField(default=False)
    nb_lecons         = models.PositiveIntegerField(default=0)
    duree_totale      = models.PositiveIntegerField(default=0, help_text="Durée en minutes")
    nb_inscrits       = models.PositiveIntegerField(default=0)
    note_moyenne      = models.FloatField(default=0.0)
    objectifs         = models.JSONField(default=list, blank=True)
    prerequis         = models.JSONField(default=list, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Formation"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    @property
    def est_gratuite(self):
        return self.prix == 0

    @property
    def thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else "/static/img/formation-default.jpg"


class Chapitre(models.Model):
    formation   = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="chapitres")
    titre       = models.CharField(max_length=200)
    ordre       = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["formation", "ordre"]
        verbose_name = "Chapitre"

    def __str__(self):
        return f"{self.formation.titre} — {self.titre}"


class Lecon(models.Model):
    TYPES = [
        ("video",  "Vidéo"),
        ("texte",  "Texte / Article"),
        ("quiz",   "Quiz"),
        ("tp",     "Travaux pratiques"),
        ("pdf",    "Document PDF"),
    ]

    chapitre     = models.ForeignKey(Chapitre, on_delete=models.CASCADE, related_name="lecons")
    titre        = models.CharField(max_length=200)
    type_lecon   = models.CharField(max_length=10, choices=TYPES, default="texte")
    contenu      = models.TextField(help_text="Contenu HTML riche")
    video_url    = models.URLField(blank=True)
    fichier_pdf  = models.FileField(upload_to="formations/pdfs/", null=True, blank=True)
    ordre        = models.PositiveIntegerField(default=0)
    duree        = models.PositiveIntegerField(default=5, help_text="Durée estimée en minutes")
    is_free      = models.BooleanField(default=False, help_text="Accessible sans inscription")
    is_published = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["chapitre", "ordre"]
        verbose_name = "Leçon"

    def __str__(self):
        return f"{self.chapitre.formation.titre} › {self.titre}"

    @property
    def formation(self):
        return self.chapitre.formation


class Quiz(models.Model):
    lecon       = models.OneToOneField(Lecon, on_delete=models.CASCADE,
                                        related_name="quiz", null=True, blank=True)
    formation   = models.ForeignKey(Formation, on_delete=models.CASCADE,
                                    related_name="quiz_finaux", null=True, blank=True)
    titre       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    score_min   = models.PositiveIntegerField(default=70, help_text="Score minimum pour réussir (%)")
    duree_min   = models.PositiveIntegerField(default=0, help_text="Durée limite en minutes (0 = illimité)")
    actif       = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"

    def __str__(self):
        return self.titre


class Question(models.Model):
    TYPES = [
        ("qcm",    "QCM (choix multiple)"),
        ("vf",     "Vrai / Faux"),
        ("courte", "Réponse courte"),
        ("longue", "Réponse longue"),
    ]

    quiz    = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    texte   = models.TextField()
    type_q  = models.CharField(max_length=10, choices=TYPES, default="qcm")
    # Pour QCM : [{"texte": "...", "correct": true/false}, ...]
    choix   = models.JSONField(default=list, blank=True)
    reponse_correcte = models.TextField(blank=True)
    explication      = models.TextField(blank=True)
    points  = models.PositiveIntegerField(default=1)
    ordre   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["quiz", "ordre"]

    def __str__(self):
        return f"Q{self.ordre}: {self.texte[:60]}"


class ResultatQuiz(models.Model):
    utilisateur  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                      related_name="resultats_quiz")
    quiz         = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score        = models.FloatField(default=0, help_text="Score en %")
    nb_bonnes    = models.PositiveIntegerField(default=0)
    nb_questions = models.PositiveIntegerField(default=0)
    reponses     = models.JSONField(default=dict, blank=True)
    termine      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.utilisateur.username} — {self.quiz.titre} ({self.score:.0f}%)"


class Inscription(models.Model):
    utilisateur      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                          related_name="inscriptions")
    formation        = models.ForeignKey(Formation, on_delete=models.CASCADE,
                                         related_name="inscriptions")
    date_inscription = models.DateTimeField(auto_now_add=True)
    progression_pct  = models.PositiveIntegerField(default=0)
    termine          = models.BooleanField(default=False)
    date_fin         = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("utilisateur", "formation")
        ordering = ["-date_inscription"]
        verbose_name = "Inscription"

    def __str__(self):
        return f"{self.utilisateur.username} → {self.formation.titre}"


class Progression(models.Model):
    utilisateur     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                         related_name="progressions_lecons")
    lecon           = models.ForeignKey(Lecon, on_delete=models.CASCADE, related_name="progressions")
    completee       = models.BooleanField(default=False)
    temps_passe     = models.PositiveIntegerField(default=0, help_text="Temps passé en secondes")
    date_completion = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("utilisateur", "lecon")

    def __str__(self):
        return f"{'✓' if self.completee else '○'} {self.utilisateur.username} — {self.lecon.titre}"


class AvisFormation(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    formation   = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name="avis")
    note        = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    commentaire = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("utilisateur", "formation")
        ordering = ["-created_at"]
        verbose_name = "Avis"
        verbose_name_plural = "Avis"

    def __str__(self):
        return f"{self.utilisateur.username} → {self.formation.titre} ({self.note}★)"


class Certificat(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     related_name="certificats")
    formation   = models.ForeignKey(Formation, on_delete=models.CASCADE)
    code_unique = models.CharField(max_length=40, unique=True)
    date_obtenu = models.DateTimeField(auto_now_add=True)
    pdf         = models.FileField(upload_to="certificats/", null=True, blank=True)

    class Meta:
        ordering = ["-date_obtenu"]
        verbose_name = "Certificat"

    def __str__(self):
        return f"Certificat {self.code_unique} — {self.utilisateur.username}"
