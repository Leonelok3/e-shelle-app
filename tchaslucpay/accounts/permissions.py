from rest_framework import permissions

from .models import UserRole


class IsAdminUser(permissions.BasePermission):
    """Autorise uniquement les utilisateurs avec le role administrateur."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) == UserRole.ADMIN)


class IsCollecteurUser(permissions.BasePermission):
    """Autorise uniquement les collecteurs authentifies."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) == UserRole.COLLECTEUR)


class IsClientUser(permissions.BasePermission):
    """Autorise uniquement les clients authentifies."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) == UserRole.CLIENT)


class IsAssignedClientForCollecteur(permissions.BasePermission):
    """Verifie qu'un collecteur accede seulement a ses propres clients."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "role", None) == UserRole.ADMIN:
            return True
        if getattr(user, "role", None) != UserRole.COLLECTEUR:
            return False

        collecteur = getattr(user, "collecteur_profile", None)
        return bool(collecteur and getattr(obj, "trusted_collecteur_id", None) == collecteur.pk)
