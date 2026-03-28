from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone

from ..models import ActeurAgro, ProduitAgro, DemandeDevis, CommandeAgro
from ..forms import DemandeDevisForm, ReponseDevisForm
from ..utils.export import generer_pdf_devis, generer_pdf_facture


@login_required
def demander_devis(request, produit_slug):
    """Formulaire de demande de devis pour un produit."""
    produit  = get_object_or_404(ProduitAgro, slug=produit_slug, statut='publie')
    acheteur = get_object_or_404(ActeurAgro, user=request.user)

    if acheteur == produit.acteur:
        messages.error(request, "Vous ne pouvez pas demander un devis pour votre propre produit.")
        return redirect('agro:produit', slug=produit_slug)

    # Vérifier limite plan free
    if acheteur.plan_premium == 'free':
        from django.utils.timezone import now
        debut_mois = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        nb_devis_mois = DemandeDevis.objects.filter(
            acheteur=acheteur,
            date_creation__gte=debut_mois
        ).count()
        if nb_devis_mois >= 3:
            messages.warning(
                request,
                "Vous avez atteint votre limite de 3 demandes de devis/mois (plan gratuit)."
            )
            return redirect('agro:premium')

    if request.method == 'POST':
        form = DemandeDevisForm(request.POST)
        if form.is_valid():
            devis = form.save(commit=False)
            devis.acheteur = acheteur
            devis.vendeur  = produit.acteur
            devis.produit  = produit
            devis.save()
            # Incrémenter le compteur de demandes du produit
            ProduitAgro.objects.filter(pk=produit.pk).update(nb_demandes=produit.nb_demandes + 1)
            messages.success(request, f"Demande de devis {devis.reference} envoyée avec succès.")
            return redirect('agro:detail_devis', reference=devis.reference)
    else:
        form = DemandeDevisForm(initial={
            'unite_mesure': produit.unite_mesure,
            'quantite':     produit.quantite_min_commande,
        })

    context = {
        'form':       form,
        'produit':    produit,
        'acheteur':   acheteur,
        'page_title': f"Demander un devis — {produit.nom} | E-Shelle Agro",
    }
    return render(request, 'agro/commandes/devis_form.html', context)


@login_required
def mes_devis(request):
    """Liste des devis de l'utilisateur connecté (envoyés + reçus)."""
    acteur = get_object_or_404(ActeurAgro, user=request.user)

    devis_envoyes = DemandeDevis.objects.filter(
        acheteur=acteur
    ).select_related('vendeur', 'produit').order_by('-date_creation')

    devis_recus = DemandeDevis.objects.filter(
        vendeur=acteur
    ).select_related('acheteur', 'produit').order_by('-date_creation')

    # Marquer comme "vus"
    devis_recus.filter(statut='en_attente').update(statut='vue')

    context = {
        'acteur':         acteur,
        'devis_envoyes':  devis_envoyes[:20],
        'devis_recus':    devis_recus[:20],
        'page_title':     "Mes Devis | E-Shelle Agro",
    }
    return render(request, 'agro/commandes/mes_devis.html', context)


@login_required
def detail_devis(request, reference):
    acteur = get_object_or_404(ActeurAgro, user=request.user)
    devis  = get_object_or_404(
        DemandeDevis.objects.select_related('acheteur', 'vendeur', 'produit'),
        reference=reference
    )

    if acteur not in [devis.acheteur, devis.vendeur]:
        return HttpResponseForbidden()

    context = {
        'devis':      devis,
        'acteur':     acteur,
        'est_vendeur': acteur == devis.vendeur,
        'page_title': f"Devis {reference} | E-Shelle Agro",
    }
    return render(request, 'agro/commandes/detail_devis.html', context)


@login_required
def repondre_devis(request, reference):
    """Le vendeur répond à une demande de devis."""
    acteur = get_object_or_404(ActeurAgro, user=request.user)
    devis  = get_object_or_404(DemandeDevis, reference=reference, vendeur=acteur)

    if request.method == 'POST':
        form = ReponseDevisForm(request.POST, instance=devis)
        if form.is_valid():
            devis = form.save(commit=False)
            devis.statut = 'devis_envoye'
            devis.save()
            messages.success(request, "Votre devis a été envoyé à l'acheteur.")
            return redirect('agro:detail_devis', reference=reference)
    else:
        form = ReponseDevisForm(instance=devis)

    context = {
        'form':       form,
        'devis':      devis,
        'page_title': f"Répondre au devis {reference} | E-Shelle Agro",
    }
    return render(request, 'agro/commandes/repondre_devis.html', context)


@login_required
def accepter_devis(request, reference):
    """L'acheteur accepte un devis et crée la commande."""
    acteur = get_object_or_404(ActeurAgro, user=request.user)
    devis  = get_object_or_404(DemandeDevis, reference=reference, acheteur=acteur)

    if devis.statut not in ['devis_envoye', 'negocie']:
        messages.error(request, "Ce devis ne peut pas être accepté dans son état actuel.")
        return redirect('agro:detail_devis', reference=reference)

    if request.method == 'POST':
        devis.statut = 'accepte'
        devis.save(update_fields=['statut'])

        commande = CommandeAgro.objects.create(
            devis=devis,
            acheteur=devis.acheteur,
            vendeur=devis.vendeur,
            montant_total=devis.prix_propose or 0,
            devise=devis.devise_propose or 'XAF',
            incoterm=devis.incoterm_souhaite or 'EXW',
        )
        # Mettre à jour les compteurs
        ActeurAgro.objects.filter(pk=devis.vendeur.pk).update(
            nb_commandes=devis.vendeur.nb_commandes + 1
        )
        messages.success(request, f"Commande {commande.numero_commande} créée avec succès !")
        return redirect('agro:detail_commande', numero=commande.numero_commande)

    context = {
        'devis':      devis,
        'page_title': "Confirmer l'acceptation du devis | E-Shelle Agro",
    }
    return render(request, 'agro/commandes/accepter_devis.html', context)


@login_required
def mes_commandes(request):
    """Liste des commandes de l'utilisateur."""
    acteur = get_object_or_404(ActeurAgro, user=request.user)

    commandes_passees = CommandeAgro.objects.filter(
        acheteur=acteur
    ).select_related('vendeur', 'devis__produit').order_by('-date_creation')

    commandes_recues = CommandeAgro.objects.filter(
        vendeur=acteur
    ).select_related('acheteur', 'devis__produit').order_by('-date_creation')

    context = {
        'acteur':            acteur,
        'commandes_passees': commandes_passees,
        'commandes_recues':  commandes_recues,
        'page_title':        "Mes Commandes | E-Shelle Agro",
    }
    return render(request, 'agro/commandes/mes_commandes.html', context)


@login_required
def detail_commande(request, numero):
    acteur   = get_object_or_404(ActeurAgro, user=request.user)
    commande = get_object_or_404(
        CommandeAgro.objects.select_related('acheteur', 'vendeur', 'devis'),
        numero_commande=numero
    )

    if acteur not in [commande.acheteur, commande.vendeur]:
        return HttpResponseForbidden()

    context = {
        'commande':    commande,
        'acteur':      acteur,
        'est_vendeur': acteur == commande.vendeur,
        'page_title':  f"Commande {numero} | E-Shelle Agro",
    }
    return render(request, 'agro/commandes/detail_commande.html', context)


@login_required
def exporter_devis_pdf(request, reference):
    acteur = get_object_or_404(ActeurAgro, user=request.user)
    devis  = get_object_or_404(DemandeDevis, reference=reference)

    if acteur not in [devis.acheteur, devis.vendeur]:
        return HttpResponseForbidden()

    pdf = generer_pdf_devis(devis)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="devis-{reference}.pdf"'
    return response


@login_required
def exporter_facture(request, numero):
    acteur   = get_object_or_404(ActeurAgro, user=request.user)
    commande = get_object_or_404(CommandeAgro, numero_commande=numero)

    if acteur not in [commande.acheteur, commande.vendeur]:
        return HttpResponseForbidden()

    pdf = generer_pdf_facture(commande)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture-{numero}.pdf"'
    return response
