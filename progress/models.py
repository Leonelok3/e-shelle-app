from django.conf import settings
from django.db import models
from content.models import Exercise, Exam

User = settings.AUTH_USER_MODEL


class Attempt(models.Model):
    ATTEMPT_TYPE_CHOICES = (
        ("exercise", "Exercise"),
        ("exam", "Exam"),
    )

    # ✅ null=True évite le prompt "default pour user"
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    attempt_type = models.CharField(
        max_length=20,
        choices=ATTEMPT_TYPE_CHOICES,
        default="exercise"  # ✅ évite le prompt
    )

    exercise = models.ForeignKey(Exercise, null=True, blank=True, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, null=True, blank=True, on_delete=models.CASCADE)

    score = models.FloatField(default=0)
    max_score = models.FloatField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        u = self.user.username if self.user else "Unknown"
        return f"{u} - {self.attempt_type} - {self.score}/{self.max_score}"


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question_text = models.TextField(default="")   # ✅ évite le prompt
    given_answer = models.TextField(default="")    # ✅ évite le prompt
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer ({self.correct})"
