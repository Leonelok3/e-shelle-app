"""
dashboard/views.py — Tableau de bord multi-rôle E-Shelle
Admin, formateur, apprenant, client.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta


@login_required
def index(request):
    """Dashboard principal — redirige selon le rôle."""
    user = request.user
    role = getattr(user, "role", "STUDENT")

    if role in ("SUPERADMIN",) or user.is_superuser:
        return _dashboard_admin(request)
    elif role == "TEACHER":
        return _dashboard_formateur(request)
    elif role == "CLIENT":
        return _dashboard_client(request)
    else:
        return _dashboard_apprenant(request)


def _dashboard_admin(request):
    """Dashboard administrateur — vue globale plateforme."""
    from formations.models import Formation, Inscription
    from boutique.models import Commande, Produit
    from accounts.models import CustomUser
    from dashboard.models import Notification
    from payments.models import Transaction

    # Stats globales
    nb_users    = CustomUser.objects.count()
    nb_formations = Formation.objects.filter(is_published=True).count()
    nb_inscrits = Inscription.objects.count()
    nb_commandes = Commande.objects.filter(statut="payee").count()

    # Revenus 30 derniers jours
    date_debut = timezone.now() - timedelta(days=30)
    revenus    = Transaction.objects.filter(
        statut="succes", created_at__gte=date_debut
    ).aggregate(total=Sum("montant"))["total"] or 0

    # Nouvelles inscriptions 7 derniers jours
    date_7j    = timezone.now() - timedelta(days=7)
    new_users  = CustomUser.objects.filter(date_joined__gte=date_7j).count()

    # Dernières transactions
    transactions = Transaction.objects.select_related(
        "utilisateur"
    ).order_by("-created_at")[:10]

    # Notifications non lues
    notifications = Notification.objects.filter(
        destinataire=request.user, lue=False
    ).order_by("-created_at")[:5]

    context = {
        "role": "admin",
        "nb_users":     nb_users,
        "nb_formations": nb_formations,
        "nb_inscrits":  nb_inscrits,
        "nb_commandes": nb_commandes,
        "revenus":      revenus,
        "new_users":    new_users,
        "transactions": transactions,
        "notifications": notifications,
    }
    return render(request, "dashboard/admin.html", context)


def _dashboard_formateur(request):
    """Dashboard formateur — ses cours et leurs stats."""
    from formations.models import Formation, Inscription, AvisFormation

    formations = Formation.objects.filter(
        formateur=request.user
    ).annotate(nb_inscriptions=Count("inscriptions")).order_by("-created_at")

    nb_apprenants = Inscription.objects.filter(
        formation__formateur=request.user
    ).values("utilisateur").distinct().count()

    note_moy = AvisFormation.objects.filter(
        formation__formateur=request.user
    ).aggregate(moy=Sum("note"))

    context = {
        "role":          "formateur",
        "formations":    formations,
        "nb_apprenants": nb_apprenants,
    }
    return render(request, "dashboard/formateur.html", context)


def _dashboard_apprenant(request):
    """Dashboard apprenant — sa progression et ses inscriptions."""
    from formations.models import Inscription, Progression, Certificat

    inscriptions = Inscription.objects.filter(
        utilisateur=request.user
    ).select_related("formation").order_by("-date_inscription")[:6]

    certificats = Certificat.objects.filter(
        utilisateur=request.user
    ).select_related("formation")

    # Streak (jours consécutifs avec une activité)
    nb_completees = Progression.objects.filter(
        utilisateur=request.user, completee=True
    ).count()

    context = {
        "role":          "apprenant",
        "inscriptions":  inscriptions,
        "certificats":   certificats,
        "nb_completees": nb_completees,
    }
    return render(request, "dashboard/apprenant.html", context)


def _dashboard_client(request):
    """Dashboard client — ses commandes et téléchargements."""
    from boutique.models import Commande, Telechargement
    from services.models import Devis

    commandes      = Commande.objects.filter(
        utilisateur=request.user
    ).order_by("-created_at")[:10]

    telechargements = Telechargement.objects.filter(
        utilisateur=request.user
    ).select_related("produit").order_by("-created_at")

    devis = Devis.objects.filter(
        utilisateur=request.user
    ).order_by("-created_at")[:5]

    context = {
        "role":            "client",
        "commandes":       commandes,
        "telechargements": telechargements,
        "devis":           devis,
    }
    return render(request, "dashboard/client.html", context)


@login_required
def notifications(request):
    """Page notifications."""
    from dashboard.models import Notification
    notifs = Notification.objects.filter(
        destinataire=request.user
    ).order_by("-created_at")[:50]
    # Marquer toutes comme lues
    Notification.objects.filter(destinataire=request.user, lue=False).update(lue=True)
    return render(request, "dashboard/notifications.html", {"notifications": notifs})
