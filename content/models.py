from django.db import models
from django.conf import settings
from curriculum.models import ClassLevel, Subject


class PublishStatus(models.TextChoices):
    DRAFT = "DRAFT", "Brouillon"
    PUBLISHED = "PUBLISHED", "Publié"


class Lesson(models.Model):
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    content = models.TextField(help_text="Contenu de la leçon (HTML ou texte)")

    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.class_level} - {self.subject})"


class Exercise(models.Model):
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=200)
    instruction = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT
    )

    def __str__(self):
        return self.title


class Exam(models.Model):
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(default=120)
    instructions = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT
    )

    def __str__(self):
        return self.title


class QuestionType(models.TextChoices):
    QCM = "QCM", "QCM"
    TRUE_FALSE = "TF", "Vrai / Faux"
    SHORT = "SHORT", "Réponse courte"


class Question(models.Model):
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, null=True, blank=True, related_name="questions"
    )
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, null=True, blank=True, related_name="questions"
    )

    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QuestionType.choices)

    choices = models.JSONField(blank=True, null=True)
    correct_answer = models.JSONField()
    explanation = models.TextField(blank=True)

    points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text[:50]


class PastPaper(models.Model):
    EXAM_TYPES = (
        ("BEPC", "BEPC"),
        ("PROBATOIRE", "Probatoire"),
        ("BAC", "Baccalauréat"),
        ("GCE", "GCE"),
    )

    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    year = models.PositiveIntegerField()
    session = models.CharField(max_length=50, blank=True)

    pdf_file = models.FileField(upload_to="past_papers/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam_type} {self.year} - {self.subject}"
