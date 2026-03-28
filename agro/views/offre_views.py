from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from ..models import (
    ActeurAgro, OffreCommerciale, AppelOffre, ReponseAppelOffre,
    CategorieAgro,
)


def liste_offres(request):
    """Liste des offres commerciales actives."""
    offres_qs = OffreCommerciale.objects.filter(
        est_active=True
    ).select_related('acteur', 'produit').order_by('-est_urgente', '-date_publication')

    # Filtres
    type_offre = request.GET.get('type')
    if type_offre:
        offres_qs = offres_qs.filter(type_offre=type_offre)

    paginator = Paginator(offres_qs, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj':    page_obj,
        'type_actif':  type_offre,
        'page_title':  'Offres Commerciales Agroalimentaires | E-Shelle Agro',
    }
    return render(request, 'agro/offres/liste_offres.html', context)


def detail_offre(request, pk):
    offre = get_object_or_404(
        OffreCommerciale.objects.select_related('acteur', 'produit'),
        pk=pk, est_active=True
    )
    OffreCommerciale.objects.filter(pk=pk).update(nb_vues=offre.nb_vues + 1)
    context = {'offre': offre, 'page_title': f"{offre.titre} | E-Shelle Agro"}
    return render(request, 'agro/offres/offre_detail.html', context)


@login_required
def creer_offre(request):
    acteur = get_object_or_404(ActeurAgro, user=request.user)

    if request.method == 'POST':
        from ..forms import ActeurAgroForm
        # Traitement simple du formulaire offre
        data = request.POST
        offre = OffreCommerciale.objects.create(
            acteur=acteur,
            type_offre=data['type_offre'],
            titre=data['titre'],
            description=data['description'],
            quantite=float(data['quantite']),
            unite_mesure=data['unite_mesure'],
            devise=data.get('devise', 'XAF'),
            date_validite=data['date_validite'],
            lieu_livraison=data.get('lieu_livraison', ''),
            conditions=data.get('conditions', ''),
            est_urgente=bool(data.get('est_urgente')),
        )
        if data.get('prix_propose'):
            offre.prix_propose = float(data['prix_propose'])
            offre.save(update_fields=['prix_propose'])
        messages.success(request, "Offre publiée avec succès.")
        return redirect('agro:detail_offre', pk=offre.pk)

    context = {
        'acteur':     acteur,
        'produits':   acteur.produits.filter(statut='publie'),
        'page_title': "Créer une offre | E-Shelle Agro",
    }
    return render(request, 'agro/offres/creer_offre.html', context)


def liste_ao(request):
    """Liste des appels d'offre publics."""
    ao_qs = AppelOffre.objects.filter(
        est_publie=True
    ).select_related('acheteur', 'categorie').order_by('-est_urgent', '-date_creation')

    categorie_slug = request.GET.get('categorie')
    if categorie_slug:
        ao_qs = ao_qs.filter(categorie__slug=categorie_slug)

    paginator = Paginator(ao_qs, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj':   page_obj,
        'categories': CategorieAgro.objects.filter(est_active=True, parent__isnull=True),
        'page_title': "Appels d'Offre | E-Shelle Agro",
    }
    return render(request, 'agro/offres/liste_ao.html', context)


def detail_ao(request, pk):
    ao = get_object_or_404(
        AppelOffre.objects.select_related('acheteur', 'categorie'),
        pk=pk, est_publie=True
    )
    reponses = ao.reponses.filter(
        statut__in=['soumise', 'en_evaluation', 'acceptee']
    ).select_related('fournisseur') if request.user.is_authenticated else []

    context = {
        'ao':         ao,
        'reponses':   reponses,
        'page_title': f"{ao.titre} | E-Shelle Agro",
    }
    return render(request, 'agro/offres/appel_offre_detail.html', context)


@login_required
def lancer_ao(request):
    acteur = get_object_or_404(ActeurAgro, user=request.user)

    if request.method == 'POST':
        data = request.POST
        ao = AppelOffre.objects.create(
            acheteur=acteur,
            titre=data['titre'],
            description=data['description'],
            quantite_min=float(data['quantite_min']),
            unite_mesure=data['unite_mesure'],
            devise=data.get('devise', 'USD'),
            date_limite_soumission=data['date_limite_soumission'],
            est_urgent=bool(data.get('est_urgent')),
        )
        if data.get('categorie'):
            ao.categorie_id = int(data['categorie'])
        if data.get('budget_max'):
            ao.budget_max = float(data['budget_max'])
        ao.save()
        messages.success(request, "Appel d'offre publié.")
        return redirect('agro:detail_ao', pk=ao.pk)

    context = {
        'acteur':     acteur,
        'categories': CategorieAgro.objects.filter(est_active=True),
        'page_title': "Lancer un appel d'offre | E-Shelle Agro",
    }
    return render(request, 'agro/offres/creer_ao.html', context)


@login_required
def repondre_ao(request, pk):
    ao     = get_object_or_404(AppelOffre, pk=pk, est_publie=True)
    acteur = get_object_or_404(ActeurAgro, user=request.user)

    if acteur == ao.acheteur:
        messages.error(request, "Vous ne pouvez pas répondre à votre propre appel d'offre.")
        return redirect('agro:detail_ao', pk=pk)

    if request.method == 'POST':
        data = request.POST
        ReponseAppelOffre.objects.create(
            appel_offre=ao,
            fournisseur=acteur,
            prix_unitaire=float(data['prix_unitaire']),
            devise=data['devise'],
            quantite_disponible=float(data['quantite_disponible']),
            delai_jours=int(data['delai_jours']),
            incoterm=data['incoterm'],
            conditions=data['conditions'],
        )
        AppelOffre.objects.filter(pk=pk).update(nb_reponses=ao.nb_reponses + 1)
        messages.success(request, "Votre réponse a été soumise avec succès.")
        return redirect('agro:detail_ao', pk=pk)

    context = {
        'ao':         ao,
        'acteur':     acteur,
        'page_title': f"Répondre à {ao.titre} | E-Shelle Agro",
    }
    return render(request, 'agro/offres/repondre_ao.html', context)
