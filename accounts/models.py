from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import random


# ─── Clés applicatives E-Shelle ──────────────────────────────────────────────

class AppKey(models.TextChoices):
    ADGEN      = "adgen",      "AdGen — Publicités IA"
    RESTO      = "resto",      "E-Shelle Resto"
    RENCONTRES = "rencontres", "E-Shelle Love"
    NJANGI     = "njangi",     "Njangi Digital"
    EDU        = "edu",        "EduCam Pro"
    FORMATIONS = "formations", "Formations"
    BOUTIQUE   = "boutique",   "Boutique"
    AGRO       = "agro",       "E-Shelle Agro"

APP_ICONS = {
    "adgen":      "✨",
    "resto":      "🍽️",
    "rencontres": "❤️",
    "njangi":     "🤝",
    "edu":        "🎓",
    "formations": "📚",
    "boutique":   "🛒",
    "agro":       "🌿",
}

APP_COLORS = {
    "adgen":      "#6C3FE8",
    "resto":      "#F97316",
    "rencontres": "#E8436A",
    "njangi":     "#1B6CA8",
    "edu":        "#0EA5E9",
    "formations": "#8B5CF6",
    "boutique":   "#10B981",
    "agro":       "#84CC16",
}


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


# ─── Plans d'abonnement par application ──────────────────────────

class AppPlan(models.Model):
    """Un plan tarifaire pour une application E-Shelle donnée."""

    LEVEL_CHOICES = [
        ("free",       "Gratuit"),
        ("trial",      "Essai"),
        ("starter",    "Starter"),
        ("pro",        "Pro"),
        ("enterprise", "Enterprise"),
    ]

    app_key      = models.CharField(max_length=30, choices=AppKey.choices, db_index=True)
    slug         = models.SlugField(max_length=60, unique=True)   # ex: "adgen-pro"
    name         = models.CharField(max_length=100)               # ex: "AdGen Pro"
    level        = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="starter")
    description  = models.TextField(blank=True)
    price_xaf    = models.PositiveIntegerField(default=0)         # 0 = gratuit
    price_eur    = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duration_days = models.PositiveIntegerField(default=30)       # 0 = illimité
    features     = models.JSONField(default=list)                 # liste de strings
    is_free      = models.BooleanField(default=False)
    is_popular   = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    order        = models.PositiveSmallIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["app_key", "order"]
        verbose_name = "Plan d'application"
        verbose_name_plural = "Plans d'application"

    def __str__(self):
        return f"{self.name} ({self.get_app_key_display()})"

    @property
    def price_xaf_formatted(self):
        if self.price_xaf == 0:
            return "Gratuit"
        return f"{self.price_xaf:,} FCFA".replace(",", " ")

    @property
    def app_icon(self):
        return APP_ICONS.get(self.app_key, "📦")

    @property
    def app_color(self):
        return APP_COLORS.get(self.app_key, "#6B7280")


# ─── Abonnements utilisateur ──────────────────────────────────────

class AppSubscription(models.Model):
    """Abonnement d'un utilisateur à un plan d'une application."""

    STATUS_CHOICES = [
        ("trial",     "Essai gratuit"),
        ("active",    "Actif"),
        ("expired",   "Expiré"),
        ("cancelled", "Annulé"),
        ("pending",   "En attente"),
    ]

    user       = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE,
        related_name="app_subscriptions"
    )
    plan       = models.ForeignKey(AppPlan, on_delete=models.PROTECT, related_name="subscriptions")
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    payment_ref = models.CharField(max_length=200, blank=True, default="")
    auto_renew = models.BooleanField(default=False)
    notes      = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"

    def __str__(self):
        return f"{self.user.username} — {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        if self.status in ("cancelled", "pending"):
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return self.status in ("active", "trial")

    @property
    def days_remaining(self):
        if not self.expires_at:
            return None
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)

    @property
    def is_expiring_soon(self):
        r = self.days_remaining
        return r is not None and r <= 7

    def check_expiry(self):
        """Marque expired si dépassé. Retourne True si statut changé."""
        if self.is_active and self.expires_at and timezone.now() > self.expires_at:
            self.status = "expired"
            self.save(update_fields=["status"])
            return True
        return False

    @classmethod
    def get_active_for_user(cls, user, app_key):
        """Retourne l'abonnement actif pour user + app, ou None."""
        subs = cls.objects.filter(
            user=user,
            plan__app_key=app_key,
        ).select_related("plan").order_by("-started_at")
        for sub in subs:
            if sub.is_active:
                return sub
        return None

    @classmethod
    def grant_free(cls, user, app_key):
        """Attribue automatiquement le plan gratuit d'une app si aucun abonnement."""
        existing = cls.objects.filter(user=user, plan__app_key=app_key).exists()
        if existing:
            return None
        try:
            plan = AppPlan.objects.get(app_key=app_key, is_free=True, is_active=True)
        except AppPlan.DoesNotExist:
            return None
        return cls.objects.create(user=user, plan=plan, status="active", expires_at=None)


# ─── Historique des paiements ─────────────────────────────────────

class PaymentHistory(models.Model):
    """Trace tous les paiements effectués sur la plateforme."""

    METHOD_CHOICES = [
        ("orange_money", "Orange Money"),
        ("mtn_momo",     "MTN MoMo"),
        ("stripe",       "Carte bancaire"),
        ("cinetpay",     "CinetPay"),
        ("manual",       "Manuel (admin)"),
        ("free",         "Gratuit"),
    ]

    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("success", "Succès"),
        ("failed",  "Échec"),
        ("refunded","Remboursé"),
    ]

    user         = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE,
        related_name="payment_history"
    )
    subscription = models.ForeignKey(
        AppSubscription, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="payments"
    )
    amount_xaf   = models.PositiveIntegerField(default=0)
    method       = models.CharField(max_length=30, choices=METHOD_CHOICES, default="manual")
    reference    = models.CharField(max_length=200, unique=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    description  = models.TextField(blank=True, default="")
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Paiement"
        verbose_name_plural = "Historique paiements"

    def __str__(self):
        return f"{self.user.username} — {self.amount_xaf} FCFA — {self.status}"

    @property
    def amount_formatted(self):
        if self.amount_xaf == 0:
            return "Gratuit"
        return f"{self.amount_xaf:,} FCFA".replace(",", " ")


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
