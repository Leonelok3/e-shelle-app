from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import random


class Role(models.TextChoices):
    SUPERADMIN = "SUPERADMIN", _("Super Admin")
    TEACHER    = "TEACHER",    _("Enseignant / Formateur")
    PARENT     = "PARENT",     _("Parent")
    STUDENT    = "STUDENT",    _("Élève / Apprenant")
    CLIENT     = "CLIENT",     _("Client / Entrepreneur")
    VENDOR     = "VENDOR",     _("Vendeur / Partenaire")


class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == Role.SUPERADMIN or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == Role.TEACHER

    @property
    def is_client(self):
        return self.role == Role.CLIENT


def avatar_upload_path(instance, filename):
    return f"avatars/{instance.user.id}/{filename}"


class UserProfile(models.Model):
    """Profil étendu pour tous les utilisateurs SaaS."""
    user       = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    avatar     = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    bio        = models.TextField(blank=True, default="")
    telephone  = models.CharField(max_length=25, blank=True, default="")
    ville      = models.CharField(max_length=100, blank=True, default="")
    pays       = models.CharField(max_length=100, blank=True, default="Cameroun")
    site_web   = models.URLField(blank=True, default="")
    # Niveau CECR (utilisé par les cours de langues)
    LEVEL_CHOICES = [
        ("A1","A1"), ("A2","A2"), ("B1","B1"),
        ("B2","B2"), ("C1","C1"), ("C2","C2"),
    ]
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, blank=True, default="A1")
    # Solde virtuel (pour programme d'affiliation, crédits IA, etc.)
    solde      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Plan souscrit
    PLANS = [("free","Gratuit"),("pro","Pro"),("enterprise","Enterprise")]
    plan       = models.CharField(max_length=20, choices=PLANS, default="free")
    plan_expiry = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        # Initiales par défaut
        initials = (self.user.first_name[:1] + self.user.last_name[:1]).upper() or self.user.username[:2].upper()
        return f"https://ui-avatars.com/api/?name={initials}&background=2E7D32&color=fff&size=128"


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


# ─── Vérification d'email par code 6 chiffres ────────────────────

class EmailVerification(models.Model):
    user        = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="email_verification"
    )
    code        = models.CharField(max_length=6)
    created_at  = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateTimeField()
    tentatives  = models.PositiveSmallIntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Vérification email"

    def __str__(self):
        return f"{self.user.email} — code:{self.code} — vérifié:{self.is_verified}"

    @property
    def est_expire(self):
        return timezone.now() > self.expires_at

    @classmethod
    def generer(cls, user):
        """Génère (ou renouvelle) un code 6 chiffres, valable 15 min."""
        code = str(random.randint(100000, 999999))
        obj, _ = cls.objects.update_or_create(
            user=user,
            defaults={
                "code":        code,
                "expires_at":  timezone.now() + timedelta(minutes=15),
                "tentatives":  0,
                "is_verified": False,
            },
        )
        return obj
