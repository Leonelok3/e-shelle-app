from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from ..models import ActeurAgro, ProduitAgro, TypeActeur, CategorieAgro, PhotoProduit
from ..forms import InscriptionActeurForm, ActeurAgroForm, ProduitAgroForm


def profil_public(request, slug):
    """Page vitrine publique d'un acteur."""
    acteur = get_object_or_404(
        ActeurAgro.objects.prefetch_related('certifications', 'produits'),
        slug=slug, est_actif=True
    )
    ActeurAgro.objects.filter(pk=acteur.pk).update(nb_vues=acteur.nb_vues + 1)

    produits = acteur.produits.filter(statut='publie').select_related('categorie')[:12]
    avis     = acteur.avis_recus.filter(est_publie=True).select_related('evaluateur')[:5]

    context = {
        'acteur':     acteur,
        'produits':   produits,
        'avis':       avis,
        'page_title': f"{acteur.nom_entreprise} — {acteur.get_type_acteur_display()} | E-Shelle Agro",
    }
    return render(request, 'agro/acteur/profil_public.html', context)


def annuaire_acteurs(request):
    """Annuaire de tous les acteurs."""
    acteurs_qs = ActeurAgro.objects.filter(est_actif=True).select_related('user')

    # Filtres
    pays = request.GET.get('pays')
    if pays:
        acteurs_qs = acteurs_qs.filter(pays__icontains=pays)

    q = request.GET.get('q')
    if q:
        acteurs_qs = acteurs_qs.filter(nom_entreprise__icontains=q)

    paginator = Paginator(acteurs_qs.order_by('-score_confiance'), 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj':    page_obj,
        'types':       TypeActeur.choices,
        'page_title':  'Annuaire des Acteurs Agroalimentaires | E-Shelle Agro',
    }
    return render(request, 'agro/acteur/annuaire.html', context)


def annuaire_par_type(request, type_acteur):
    """Annuaire filtré par type d'acteur."""
    acteurs_qs = ActeurAgro.objects.filter(
        est_actif=True, type_acteur=type_acteur
    ).select_related('user').order_by('-score_confiance')

    paginator = Paginator(acteurs_qs, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    type_label = dict(TypeActeur.choices).get(type_acteur, type_acteur)
    context = {
        'page_obj':   page_obj,
        'type_acteur': type_acteur,
        'type_label':  type_label,
        'page_title':  f"{type_label}s — Annuaire | E-Shelle Agro",
    }
    return render(request, 'agro/acteur/annuaire.html', context)


@login_required
def inscription_acteur(request):
    """Inscription / création du profil acteur en 3 étapes."""
    # Vérifier que l'utilisateur n'a pas déjà un profil
    if hasattr(request.user, 'profil_agro'):
        messages.info(request, "Vous avez déjà un profil agro.")
        return redirect('agro:dashboard')

    etape = int(request.GET.get('etape', 1))

    if request.method == 'POST':
        form = InscriptionActeurForm(request.POST, request.FILES)
        if form.is_valid():
            acteur = form.save(commit=False)
            acteur.user = request.user
            acteur.save()
            messages.success(request, f"Bienvenue sur E-Shelle Agro, {acteur.nom_entreprise} !")
            return redirect('agro:dashboard')
    else:
        form = InscriptionActeurForm()

    context = {
        'form':       form,
        'etape':      etape,
        'page_title': "Rejoindre E-Shelle Agro | Inscription",
    }
    return render(request, 'agro/acteur/inscription.html', context)


@login_required
def modifier_profil(request):
    """Modifier son profil acteur."""
    acteur = get_object_or_404(ActeurAgro, user=request.user)

    if request.method == 'POST':
        form = ActeurAgroForm(request.POST, request.FILES, instance=acteur)
        if form.is_valid():
            acteur = form.save()
            acteur.calculer_profil_complet()
            acteur.save(update_fields=['profil_complet'])
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('agro:profil', slug=acteur.slug)
    else:
        form = ActeurAgroForm(instance=acteur)

    context = {
        'form':       form,
        'acteur':     acteur,
        'page_title': "Modifier mon profil | E-Shelle Agro",
    }
    return render(request, 'agro/acteur/profil_edit.html', context)


@login_required
def mes_produits(request):
    """Liste des produits du producteur connecté."""
    acteur   = get_object_or_404(ActeurAgro, user=request.user)
    produits = acteur.produits.select_related('categorie').order_by('-date_creation')

    paginator = Paginator(produits, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    context = {
        'acteur':     acteur,
        'page_obj':   page_obj,
        'page_title': "Mes Produits | E-Shelle Agro",
    }
    return render(request, 'agro/dashboard/mes_produits.html', context)


@login_required
def ajouter_produit(request):
    """Ajouter un nouveau produit."""
    acteur = get_object_or_404(ActeurAgro, user=request.user)

    # Vérifier limite plan free (5 produits max)
    if acteur.plan_premium == 'free':
        if acteur.produits.exclude(statut='archive').count() >= 5:
            messages.warning(
                request,
                "Vous avez atteint la limite de 5 produits avec le plan gratuit. "
                "Passez au plan Silver pour en ajouter davantage."
            )
            return redirect('agro:premium')

    if request.method == 'POST':
        form = ProduitAgroForm(request.POST, request.FILES)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.acteur = acteur
            produit.save()
            # Mettre à jour le compteur
            ActeurAgro.objects.filter(pk=acteur.pk).update(
                nb_produits=acteur.produits.count()
            )
            messages.success(request, f"Produit « {produit.nom} » ajouté. En attente de validation.")
            return redirect('agro:mes_produits')
    else:
        form = ProduitAgroForm()

    context = {
        'form':       form,
        'acteur':     acteur,
        'page_title': "Ajouter un produit | E-Shelle Agro",
    }
    return render(request, 'agro/dashboard/produit_form.html', context)


@login_required
def modifier_produit(request, slug):
    """Modifier un produit existant."""
    acteur  = get_object_or_404(ActeurAgro, user=request.user)
    produit = get_object_or_404(ProduitAgro, slug=slug)

    if produit.acteur != acteur:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier ce produit.")

    if request.method == 'POST':
        form = ProduitAgroForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit mis à jour.")
            return redirect('agro:mes_produits')
    else:
        form = ProduitAgroForm(instance=produit)

    context = {
        'form':       form,
        'produit':    produit,
        'acteur':     acteur,
        'page_title': f"Modifier {produit.nom} | E-Shelle Agro",
    }
    return render(request, 'agro/dashboard/produit_form.html', context)


@login_required
def supprimer_produit(request, slug):
    """Supprimer (archiver) un produit."""
    acteur  = get_object_or_404(ActeurAgro, user=request.user)
    produit = get_object_or_404(ProduitAgro, slug=slug)

    if produit.acteur != acteur:
        return HttpResponseForbidden()

    if request.method == 'POST':
        produit.statut = 'archive'
        produit.save(update_fields=['statut'])
        messages.success(request, f"Produit « {produit.nom} » archivé.")
        return redirect('agro:mes_produits')

    context = {'produit': produit}
    return render(request, 'agro/dashboard/confirmer_suppression.html', context)


@login_required
def gerer_photos_produit(request, pk):
    """Gérer les photos d'un produit."""
    produit = get_object_or_404(ProduitAgro, pk=pk)
    acteur  = get_object_or_404(ActeurAgro, user=request.user)

    if produit.acteur != acteur:
        return HttpResponseForbidden()

    if request.method == 'POST':
        max_photos = getattr(settings, 'AGRO_SETTINGS', {}).get('PHOTOS_MAX_PAR_PRODUIT', 8)
        if produit.photos.count() >= max_photos:
            messages.warning(request, f"Maximum {max_photos} photos par produit.")
        else:
            for f in request.FILES.getlist('photos'):
                if f.size > 5 * 1024 * 1024:  # 5 Mo max
                    messages.error(request, f"Photo {f.name} trop lourde (max 5 Mo).")
                    continue
                PhotoProduit.objects.create(produit=produit, image=f)
            messages.success(request, "Photos ajoutées.")
        return redirect('agro:photos_produit', pk=pk)

    context = {
        'produit': produit,
        'photos':  produit.photos.all(),
    }
    return render(request, 'agro/dashboard/photos_produit.html', context)
