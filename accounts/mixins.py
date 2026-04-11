"""
accounts/mixins.py
==================
Mixins réutilisables pour la gestion des abonnements E-Shelle.

Usage dans n'importe quelle vue Django :

    from accounts.mixins import SubscriptionRequiredMixin

    class MyProView(SubscriptionRequiredMixin, View):
        required_app   = "adgen"        # clé de l'app
        required_level = "pro"          # niveau minimum requis
        upgrade_message = "Passez Pro pour accéder à cette fonctionnalité."
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse

from .models import AppSubscription, AppPlan

# Ordre hiérarchique des niveaux
PLAN_LEVEL_ORDER = {
    "free":       0,
    "trial":      1,
    "starter":    2,
    "pro":        3,
    "enterprise": 4,
}


class SubscriptionRequiredMixin(LoginRequiredMixin):
    """
    Vérifie que l'utilisateur possède un abonnement actif pour `required_app`.
    Si `required_level` est défini, vérifie aussi le niveau minimum.

    Attributs à surcharger dans la sous-classe :
        required_app      (str)  — clé app ex: "adgen"
        required_level    (str)  — niveau min ex: "pro" (optionnel)
        upgrade_message   (str)  — message affiché si upgrade requis
        redirect_on_fail  (str)  — URL de redirection si non abonné
                                   (défaut : page upgrade de l'app)
    """

    required_app: str | None     = None
    required_level: str | None   = None
    upgrade_message: str         = "Abonnez-vous pour accéder à cette fonctionnalité."
    redirect_on_fail: str | None = None

    def dispatch(self, request, *args, **kwargs):
        # 1. Vérification connexion (délégué à LoginRequiredMixin)
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # 2. Superadmin passe toujours
        if request.user.is_superuser or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)

        # 3. Vérification abonnement si required_app défini
        if self.required_app:
            sub = AppSubscription.get_active_for_user(request.user, self.required_app)

            if sub is None:
                # Aucun abonnement actif
                messages.warning(request, self.upgrade_message)
                return redirect(self._get_redirect_url())

            # 4. Vérification niveau minimum
            if self.required_level:
                user_level   = PLAN_LEVEL_ORDER.get(sub.plan.level, 0)
                needed_level = PLAN_LEVEL_ORDER.get(self.required_level, 0)
                if user_level < needed_level:
                    messages.warning(request, self.upgrade_message)
                    return redirect(self._get_redirect_url())

        return super().dispatch(request, *args, **kwargs)

    def _get_redirect_url(self):
        if self.redirect_on_fail:
            return self.redirect_on_fail
        if self.required_app:
            return reverse("accounts:upgrade") + f"?app={self.required_app}"
        return reverse("accounts:mon_compte")


class AppAccessMixin(LoginRequiredMixin):
    """
    Version allégée : vérifie simplement qu'un abonnement actif existe
    pour required_app, sans contrainte de niveau.
    Redirige vers la page d'upgrade si absent.
    """

    required_app: str | None = None
    upgrade_message: str     = "Accès réservé aux abonnés."

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)

        if self.required_app:
            sub = AppSubscription.get_active_for_user(request.user, self.required_app)
            if sub is None:
                messages.warning(request, self.upgrade_message)
                url = reverse("accounts:upgrade") + f"?app={self.required_app}"
                return redirect(url)

        return super().dispatch(request, *args, **kwargs)


def user_has_subscription(user, app_key, min_level=None):
    """
    Fonction utilitaire pour vérifier dans les vues FBV ou les templates (via tag).

    Exemples :
        if user_has_subscription(request.user, "adgen"):
            ...
        if user_has_subscription(request.user, "rencontres", min_level="gold"):
            ...
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True

    sub = AppSubscription.get_active_for_user(user, app_key)
    if sub is None:
        return False

    if min_level:
        user_level   = PLAN_LEVEL_ORDER.get(sub.plan.level, 0)
        needed_level = PLAN_LEVEL_ORDER.get(min_level, 0)
        return user_level >= needed_level

    return True
