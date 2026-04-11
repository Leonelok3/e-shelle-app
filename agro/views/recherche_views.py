from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from ..models import ProduitAgro, ActeurAgro
from ..utils.recherche import filtrer_produits
from ..utils.conversion import convertir_prix


def recherche(request):
    """Page de recherche avancée."""
    q          = request.GET.get('q', '').strip()
    produits_qs = ProduitAgro.objects.filter(statut='publie').select_related('acteur', 'categorie')

    if q:
        from django.db.models import Q
        produits_qs = produits_qs.filter(
            Q(nom__icontains=q) |
            Q(nom_local__icontains=q) |
            Q(description__icontains=q) |
            Q(acteur__nom_entreprise__icontains=q) |
            Q(origine_geographique__icontains=q)
        )

    produits_qs = filtrer_produits(produits_qs, request.GET)

    paginator   = Paginator(produits_qs, 24)
    page_obj    = paginator.get_page(request.GET.get('page', 1))

    # Acteurs correspondants
    acteurs = []
    if q:
        acteurs = ActeurAgro.objects.filter(
            est_actif=True,
            nom_entreprise__icontains=q
        )[:6]

    context = {
        'q':        q,
        'page_obj': page_obj,
        'acteurs':  acteurs,
        'total':    produits_qs.count(),
        'page_title': f"Recherche : {q} | E-Shelle Agro" if q else "Recherche | E-Shelle Agro",
    }
    return render(request, 'agro/recherche.html', context)


@require_GET
def ajax_recherche(request):
    """Recherche AJAX en temps réel (autocomplete)."""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'produits': [], 'acteurs': []})

    from django.db.models import Q
    produits = ProduitAgro.objects.filter(
        statut='publie'
    ).filter(
        Q(nom__icontains=q) | Q(nom_local__icontains=q)
    ).select_related('acteur')[:6]

    acteurs = ActeurAgro.objects.filter(
        est_actif=True,
        nom_entreprise__icontains=q
    )[:4]

    data = {
        'produits': [
            {
                'nom':   p.nom,
                'slug':  p.slug,
                'acteur': p.acteur.nom_entreprise,
                'prix':   str(p.prix_unitaire),
                'devise': p.devise,
                'image':  p.image_principale.url if p.image_principale else '',
            }
            for p in produits
        ],
        'acteurs': [
            {
                'nom':  a.nom_entreprise,
                'slug': a.slug,
                'type': a.get_type_acteur_display(),
                'pays': a.pays,
            }
            for a in acteurs
        ],
    }
    return JsonResponse(data)


@login_required
def ajax_favoris(request, produit_id):
    """Toggle favori sur un produit."""
    try:
        acteur  = request.user.profil_agro
        produit = ProduitAgro.objects.get(pk=produit_id, statut='publie')
    except (ActeurAgro.DoesNotExist, ProduitAgro.DoesNotExist):
        return JsonResponse({'error': 'Non trouvé'}, status=404)

    if acteur in produit.favoris.all():
        produit.favoris.remove(acteur)
        produit.nb_favoris = max(0, produit.nb_favoris - 1)
        produit.save(update_fields=['nb_favoris'])
        est_favori = False
    else:
        produit.favoris.add(acteur)
        produit.nb_favoris += 1
        produit.save(update_fields=['nb_favoris'])
        est_favori = True

    return JsonResponse({'est_favori': est_favori, 'nb_favoris': produit.nb_favoris})


@login_required
def ajax_contact(request, slug):
    """Enregistrement d'un contact vendeur."""
    from ..models import OffreCommerciale
    try:
        acteur = ActeurAgro.objects.get(slug=slug, est_actif=True)
        ActeurAgro.objects.filter(pk=acteur.pk).update(nb_vues=acteur.nb_vues + 1)
        return JsonResponse({
            'telephone': acteur.telephone,
            'whatsapp':  acteur.whatsapp,
            'email':     acteur.email_pro,
        })
    except ActeurAgro.DoesNotExist:
        return JsonResponse({'error': 'Introuvable'}, status=404)


@require_GET
def ajax_convertir(request):
    """Conversion de prix entre devises."""
    try:
        montant = float(request.GET.get('montant', 0))
        source  = request.GET.get('source', 'XAF')
        cible   = request.GET.get('cible', 'EUR')
        resultat = convertir_prix(montant, source, cible)
        return JsonResponse({'montant': resultat, 'devise': cible})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def ajax_stats_produit(request, slug):
    """Stats publiques d'un produit."""
    try:
        p = ProduitAgro.objects.get(slug=slug, statut='publie')
        return JsonResponse({
            'nb_vues':    p.nb_vues,
            'nb_demandes': p.nb_demandes,
            'note':       p.note_moyenne,
        })
    except ProduitAgro.DoesNotExist:
        return JsonResponse({'error': 'Non trouvé'}, status=404)
