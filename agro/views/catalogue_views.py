from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from ..models import (
    CategorieAgro, ProduitAgro, ActeurAgro,
    OffreCommerciale, AppelOffre,
)
from ..utils.recherche import filtrer_produits

PRODUITS_PAR_PAGE = getattr(settings, 'AGRO_SETTINGS', {}).get('PRODUITS_PAR_PAGE', 24)


def accueil_agro(request):
    """Page d'accueil de la marketplace agroalimentaire."""
    categories = CategorieAgro.objects.filter(
        est_active=True, parent__isnull=True
    ).prefetch_related('sous_categories')

    produits_vedette = ProduitAgro.objects.filter(
        statut='publie', est_mis_en_avant=True
    ).select_related('acteur', 'categorie').prefetch_related('photos')[:8]

    if produits_vedette.count() < 4:
        produits_vedette = ProduitAgro.objects.filter(
            statut='publie'
        ).select_related('acteur', 'categorie').order_by('-nb_vues')[:8]

    acteurs_vedettes = ActeurAgro.objects.filter(
        est_actif=True, est_verifie=True
    ).order_by('-score_confiance')[:6]

    appels_urgents = AppelOffre.objects.filter(
        est_publie=True, est_urgent=True
    ).select_related('acheteur', 'categorie')[:5]

    offres_recentes = OffreCommerciale.objects.filter(
        est_active=True
    ).select_related('acteur', 'produit').order_by('-est_urgente', '-date_publication')[:5]

    # Stats globales
    stats = {
        'nb_producteurs':  ActeurAgro.objects.filter(est_actif=True).count(),
        'nb_produits':     ProduitAgro.objects.filter(statut='publie').count(),
        'nb_pays':         ActeurAgro.objects.values('pays').distinct().count(),
    }

    context = {
        'categories':       categories,
        'produits_vedette': produits_vedette,
        'acteurs_vedettes': acteurs_vedettes,
        'appels_urgents':   appels_urgents,
        'offres_recentes':  offres_recentes,
        'stats':            stats,
        'page_title':       'E-Shelle Agro — Marketplace Agroalimentaire Africaine',
    }
    return render(request, 'agro/accueil.html', context)


def catalogue(request):
    """Catalogue produits avec filtres avancés."""
    produits_qs = ProduitAgro.objects.filter(
        statut='publie'
    ).select_related('acteur', 'categorie').prefetch_related('photos')

    produits_qs = filtrer_produits(produits_qs, request.GET)

    paginator   = Paginator(produits_qs, PRODUITS_PAR_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj    = paginator.get_page(page_number)

    categories  = CategorieAgro.objects.filter(est_active=True, parent__isnull=True)

    context = {
        'page_obj':    page_obj,
        'categories':  categories,
        'params':      request.GET,
        'total':       produits_qs.count(),
        'page_title':  'Catalogue Produits Agroalimentaires | E-Shelle Agro',
    }
    return render(request, 'agro/catalogue.html', context)


def categorie(request, slug):
    """Produits d'une catégorie spécifique."""
    cat = get_object_or_404(CategorieAgro, slug=slug, est_active=True)

    # Inclure sous-catégories
    if cat.parent is None:
        cats_ids = list(cat.sous_categories.values_list('id', flat=True)) + [cat.id]
    else:
        cats_ids = [cat.id]

    produits_qs = ProduitAgro.objects.filter(
        statut='publie', categorie_id__in=cats_ids
    ).select_related('acteur', 'categorie').prefetch_related('photos')

    produits_qs = filtrer_produits(produits_qs, request.GET)

    paginator   = Paginator(produits_qs, PRODUITS_PAR_PAGE)
    page_obj    = paginator.get_page(request.GET.get('page', 1))

    context = {
        'categorie':  cat,
        'page_obj':   page_obj,
        'total':      produits_qs.count(),
        'page_title': f"{cat.nom} — E-Shelle Agro",
    }
    return render(request, 'agro/catalogue.html', context)


def detail_produit(request, slug):
    """Page détaillée d'un produit."""
    produit = get_object_or_404(
        ProduitAgro.objects.select_related('acteur', 'categorie')
                           .prefetch_related('photos', 'acteur__certifications'),
        slug=slug, statut='publie'
    )

    # Incrémenter le compteur de vues (simple)
    ProduitAgro.objects.filter(pk=produit.pk).update(nb_vues=produit.nb_vues + 1)

    # Produits similaires
    similaires = ProduitAgro.objects.filter(
        statut='publie',
        categorie=produit.categorie,
    ).exclude(pk=produit.pk).select_related('acteur')[:6]

    # Vérifier si l'utilisateur a un profil agro
    profil_acheteur = None
    if request.user.is_authenticated:
        try:
            profil_acheteur = request.user.profil_agro
        except ActeurAgro.DoesNotExist:
            pass

    context = {
        'produit':         produit,
        'similaires':      similaires,
        'profil_acheteur': profil_acheteur,
        'page_title':      produit.meta_titre or f"{produit.nom} | E-Shelle Agro",
        'meta_description': produit.meta_description,
        'og_image':        produit.image_principale.url if produit.image_principale else '',
    }
    return render(request, 'agro/produit_detail.html', context)
