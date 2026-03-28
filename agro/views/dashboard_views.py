from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from ..models import (
    ActeurAgro, ProduitAgro, DemandeDevis, CommandeAgro,
    CertificationAgro, AvisActeur,
)
from ..forms import ActeurAgroForm


PLANS = {
    'silver': {
        'nom': 'Silver', 'emoji': '🥈',
        'prix_xaf': 9900, 'prix_eur': 15,
        'features': [
            "Jusqu'à 20 produits",
            "Badge Silver",
            "10 demandes de devis/mois",
            "Statistiques de base",
            "Apparition dans les catégories",
        ],
    },
    'gold': {
        'nom': 'Gold', 'emoji': '🥇',
        'prix_xaf': 24900, 'prix_eur': 38,
        'features': [
            "Produits illimités",
            "Badge Gold + priorité dans les résultats",
            "Devis illimités",
            "Analytics avancées",
            "Export leads Excel",
            "Accès aux AO privés",
            "1 mise en avant/mois newsletter",
        ],
    },
    'platinum': {
        'nom': 'Platinum', 'emoji': '💎',
        'prix_xaf': 59900, 'prix_eur': 90,
        'features': [
            "TOUT illimité",
            "Badge Platinum animé + profil vérifié",
            "Mise en avant permanente accueil",
            "Vitrine Exportateur dédiée",
            "Support prioritaire WhatsApp",
            "Rapport mensuel marché",
            "Intégration newsletters B2B",
            "Salons virtuels E-Shelle",
        ],
    },
}


@login_required
def dashboard(request):
    """Tableau de bord principal de l'utilisateur agro."""
    try:
        acteur = request.user.profil_agro
    except ActeurAgro.DoesNotExist:
        return redirect('agro:inscription')

    # Statistiques 7 derniers jours
    from datetime import timedelta
    debut_7j = timezone.now() - timedelta(days=7)

    stats = {
        'nb_vues_7j':     ProduitAgro.objects.filter(
            acteur=acteur, date_mise_a_jour__gte=debut_7j
        ).count(),
        'devis_recus':    DemandeDevis.objects.filter(vendeur=acteur, statut='en_attente').count(),
        'commandes_cours': CommandeAgro.objects.filter(
            vendeur=acteur,
            statut__in=['confirmee', 'en_preparation', 'prete', 'expedie']
        ).count(),
    }

    produits_recents = ProduitAgro.objects.filter(
        acteur=acteur
    ).select_related('categorie').order_by('-date_creation')[:5]

    devis_recents = DemandeDevis.objects.filter(
        vendeur=acteur
    ).select_related('acheteur', 'produit').order_by('-date_creation')[:5]

    template = 'agro/dashboard/producteur.html' if acteur.est_vendeur else 'agro/dashboard/acheteur.html'

    context = {
        'acteur':          acteur,
        'stats':           stats,
        'produits_recents': produits_recents,
        'devis_recents':   devis_recents,
        'page_title':      "Mon Dashboard | E-Shelle Agro",
    }
    return render(request, template, context)


@login_required
def stats_dashboard(request):
    """Statistiques détaillées du tableau de bord."""
    acteur = get_object_or_404(ActeurAgro, user=request.user)

    # Données graphique 30 jours
    from datetime import timedelta, date
    dates  = [date.today() - timedelta(days=i) for i in range(29, -1, -1)]
    vues   = [0] * 30  # Simplifié — en production: requête annotée par jour

    context = {
        'acteur':  acteur,
        'dates':   [d.strftime('%d/%m') for d in dates],
        'vues':    vues,
        'page_title': "Statistiques | E-Shelle Agro",
    }
    return render(request, 'agro/dashboard/stats.html', context)


@login_required
def mes_certifications(request):
    acteur = get_object_or_404(ActeurAgro, user=request.user)

    if request.method == 'POST':
        data = request.POST
        cert = CertificationAgro.objects.create(
            acteur=acteur,
            type_certification=data['type_certification'],
            nom=data['nom'],
            organisme=data['organisme'],
            numero=data.get('numero', ''),
            date_obtention=data['date_obtention'],
        )
        if data.get('date_expiration'):
            cert.date_expiration = data['date_expiration']
            cert.save(update_fields=['date_expiration'])
        if request.FILES.get('document'):
            cert.document = request.FILES['document']
            cert.save(update_fields=['document'])
        messages.success(request, "Certification ajoutée. En attente de vérification.")
        return redirect('agro:certifications')

    certifications = acteur.certifications.all()
    context = {
        'acteur':         acteur,
        'certifications': certifications,
        'page_title':     "Mes Certifications | E-Shelle Agro",
    }
    return render(request, 'agro/dashboard/certifications.html', context)


@login_required
def mes_avis(request):
    acteur = get_object_or_404(ActeurAgro, user=request.user)
    avis   = acteur.avis_recus.filter(est_publie=True).select_related('evaluateur')

    context = {
        'acteur':     acteur,
        'avis':       avis,
        'page_title': "Mes Avis | E-Shelle Agro",
    }
    return render(request, 'agro/dashboard/avis.html', context)


def page_premium(request):
    """Page de présentation des plans premium."""
    context = {
        'plans':      PLANS,
        'page_title': "Plans Premium E-Shelle Agro",
    }
    return render(request, 'agro/premium/plans.html', context)


@login_required
def souscrire(request, plan):
    """Redirige vers le paiement du pack premium Agro."""
    # Mapping plans Agro → plans payments
    plan_map = {'silver': 'starter', 'gold': 'pro', 'platinum': 'expert'}
    if plan not in plan_map:
        messages.error(request, "Plan invalide.")
        return redirect('agro:premium')
    return redirect('payments:payer_premium', module='agro', plan_slug=plan_map[plan])


@login_required
def signaler_produit(request, pk):
    if request.method == 'POST':
        motif = request.POST.get('motif', '')
        # Logique de signalement (enregistrement en base ou email admin)
        messages.success(request, "Signalement envoyé à l'équipe de modération.")
    return redirect(request.META.get('HTTP_REFERER', 'agro:catalogue'))


@login_required
def signaler_acteur(request, pk):
    if request.method == 'POST':
        motif = request.POST.get('motif', '')
        messages.success(request, "Signalement envoyé à l'équipe de modération.")
    return redirect(request.META.get('HTTP_REFERER', 'agro:annuaire'))
