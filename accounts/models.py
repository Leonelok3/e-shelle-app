from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    SUPERADMIN = "SUPERADMIN", _("Super Admin")
    TEACHER = "TEACHER", _("Enseignant")
    PARENT = "PARENT", _("Parent")
    STUDENT = "STUDENT", _("Élève")


class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)

    def __str__(self):
        return f"{self.username} ({self.role})"


class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="student_profile")
    class_level = models.ForeignKey("curriculum.ClassLevel", on_delete=models.PROTECT, null=True, blank=True)
    series = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"Profil élève: {self.user.username}"


class ParentStudentLink(models.Model):
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="children_links")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="parent_links")

    class Meta:
        unique_together = ("parent", "student")

    def __str__(self):
        return f"{self.parent.username} -> {self.student.username}"
