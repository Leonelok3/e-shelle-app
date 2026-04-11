"""
Njangi+ — Modèles Groupe & Membres
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Group(models.Model):
    """Tontine/Njangi — groupe de cotisation."""

    FREQUENCY_CHOICES = [
        ("weekly",    "Hebdomadaire"),
        ("biweekly",  "Bimensuel"),
        ("monthly",   "Mensuel"),
    ]
    STATUS_CHOICES = [
        ("active",  "Actif"),
        ("paused",  "En pause"),
        ("closed",  "Clôturé"),
    ]

    # ── Identité ──────────────────────────────────────────────────────────────
    name        = models.CharField(max_length=120, verbose_name="Nom du groupe")
    slug        = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    logo        = models.ImageField(
        upload_to="njangi/logos/", null=True, blank=True, verbose_name="Logo"
    )
    invite_code = models.CharField(
        max_length=8, unique=True, blank=True,
        verbose_name="Code d'invitation",
        help_text="Code à 8 caractères pour rejoindre le groupe"
    )

    # ── Configuration financière ───────────────────────────────────────────────
    frequency           = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="monthly", verbose_name="Fréquence des séances")
    contribution_amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Cotisation par séance (FCFA)")
    max_members         = models.PositiveIntegerField(default=20, verbose_name="Nombre max de membres")

    # Taux appliqués au fond commun
    fund_loan_rate    = models.DecimalField(max_digits=5, decimal_places=2, default=10, verbose_name="Taux intérêt prêts (%/mois)")
    fund_deposit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5,  verbose_name="Taux intérêt dépôts (%/mois)")
    penalty_per_day   = models.DecimalField(max_digits=10, decimal_places=0, default=500, verbose_name="Pénalité retard (FCFA/jour)")

    # Règles de sécurité
    max_loan_multiplier   = models.PositiveSmallIntegerField(default=3, verbose_name="Emprunt max (x cotisation)", help_text="Un membre peut emprunter au max N fois sa cotisation")
    fund_reserve_pct      = models.PositiveSmallIntegerField(default=20, verbose_name="Réserve min fond commun (%)")
    require_guarantor     = models.BooleanField(default=True, verbose_name="Garant obligatoire pour prêt")

    # ── Calendrier ────────────────────────────────────────────────────────────
    start_date         = models.DateField(verbose_name="Date de début du cycle")
    next_session_date  = models.DateField(null=True, blank=True, verbose_name="Prochaine séance")
    current_cycle      = models.PositiveIntegerField(default=1, verbose_name="Cycle en cours")

    # ── État ──────────────────────────────────────────────────────────────────
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="njangi_groups_created", verbose_name="Créateur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Groupe Njangi"
        verbose_name_plural = "Groupes Njangi"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            self.slug = base
            n = 1
            while Group.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"
                n += 1
        if not self.invite_code:
            import random, string
            self.invite_code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
        super().save(*args, **kwargs)

    # ── Propriétés calculées ──────────────────────────────────────────────────

    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()

    @property
    def fund_balance(self):
        """Solde actuel du fond commun."""
        from njangi.models.fund import FundTransaction
        from django.db.models import Sum
        result = FundTransaction.objects.filter(group=self).aggregate(
            total=Sum("signed_amount")
        )
        return result["total"] or 0

    @property
    def fund_available_for_loans(self):
        """Fond disponible pour nouveaux prêts (après réserve)."""
        balance = self.fund_balance
        reserve = balance * self.fund_reserve_pct / 100
        return max(0, balance - reserve)

    @property
    def frequency_label(self):
        return dict(self.FREQUENCY_CHOICES).get(self.frequency, "")

    @property
    def formatted_contribution(self):
        return f"{int(self.contribution_amount):,}".replace(",", " ") + " FCFA"


class Membership(models.Model):
    """Appartenance d'un utilisateur à un groupe Njangi."""

    ROLE_CHOICES = [
        ("president",  "Président"),
        ("treasurer",  "Trésorier"),
        ("secretary",  "Secrétaire"),
        ("member",     "Membre"),
    ]

    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="njangi_memberships", verbose_name="Membre"
    )
    group      = models.ForeignKey(
        Group, on_delete=models.CASCADE,
        related_name="memberships", verbose_name="Groupe"
    )
    role       = models.CharField(max_length=15, choices=ROLE_CHOICES, default="member")
    hand_order = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name="Ordre de la main",
        help_text="Position dans le tour de rotation (1 = premier à recevoir)"
    )
    join_date  = models.DateField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)

    # Totaux dénormalisés (mis à jour par signaux)
    total_contributed = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="Total cotisé (FCFA)")
    total_received    = models.DecimalField(max_digits=14, decimal_places=0, default=0, verbose_name="Total reçu — mains (FCFA)")
    total_penalties   = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Total pénalités payées (FCFA)")

    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"
        unique_together = ("user", "group")
        ordering = ["hand_order", "join_date"]

    def __str__(self):
        return f"{self.user} — {self.group.name} ({self.get_role_display()})"

    @property
    def is_bureau(self):
        return self.role in ("president", "treasurer", "secretary")

    @property
    def max_loan_amount(self):
        return self.group.contribution_amount * self.group.max_loan_multiplier

    @property
    def active_loan(self):
        return self.loans.filter(status="active").first()

    @property
    def pending_contributions(self):
        from njangi.models.session import Contribution
        return Contribution.objects.filter(
            membership=self, status__in=("pending", "late")
        ).count()
