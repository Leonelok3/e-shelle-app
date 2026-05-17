from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from tchaslucpay.accounts.models import UserRole


def _redirect_to_user_space(user):
    """Retourne la page naturelle de l'utilisateur connecte."""
    if getattr(user, "role", None) == UserRole.COLLECTEUR:
        return "tchaslucpay_dashboard:collecteur"
    if getattr(user, "role", None) == UserRole.CLIENT:
        return "tchaslucpay_dashboard:client"
    return "tchaslucpay_dashboard:home"


class CollecteurRequiredMixin(LoginRequiredMixin):
    """Mixin de securite pour les vues reservees aux collecteurs."""

    def dispatch(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != UserRole.COLLECTEUR:
            messages.error(request, "Acces reserve aux collecteurs.")
            return redirect(_redirect_to_user_space(request.user))
        return super().dispatch(request, *args, **kwargs)


class ClientRequiredMixin(LoginRequiredMixin):
    """Mixin de securite pour les vues reservees aux clients."""

    def dispatch(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != UserRole.CLIENT:
            messages.error(request, "Acces reserve aux clients.")
            return redirect(_redirect_to_user_space(request.user))
        return super().dispatch(request, *args, **kwargs)


def collecteur_required(view_func):
    """Decorateur equivalent au mixin pour les vues fonctionnelles collecteur."""

    def wrapped(request, *args, **kwargs):
        if getattr(request.user, "role", None) != UserRole.COLLECTEUR:
            messages.error(request, "Acces reserve aux collecteurs.")
            return redirect(_redirect_to_user_space(request.user))
        return view_func(request, *args, **kwargs)

    return wrapped


def client_required(view_func):
    """Decorateur equivalent au mixin pour les vues fonctionnelles client."""

    def wrapped(request, *args, **kwargs):
        if getattr(request.user, "role", None) != UserRole.CLIENT:
            messages.error(request, "Acces reserve aux clients.")
            return redirect(_redirect_to_user_space(request.user))
        return view_func(request, *args, **kwargs)

    return wrapped
