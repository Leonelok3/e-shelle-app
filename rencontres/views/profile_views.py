from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.db.models import Q

from rencontres.models import ProfilRencontre, PhotoProfil, Like, Match
from rencontres.forms import ProfilRencontreForm, PhotoProfilForm
from rencontres.utils.notifications import get_stats_notifications


def profil_requis(vue):
    """Décorateur : redirige vers creer_profil si pas de profil rencontre."""
    from functools import wraps

    @wraps(vue)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profil_rencontre'):
            messages.info(request, "Créez votre profil de rencontre pour continuer.")
            return redirect('rencontres:creer_profil')
        return vue(request, *args, **kwargs)
    return wrapper


@login_required
def accueil_rencontre(request):
    """Page d'entrée de l'app rencontres."""
    if hasattr(request.user, 'profil_rencontre'):
        return redirect('rencontres:decouverte')
    return render(request, 'rencontres/accueil.html')


@login_required
def creer_profil(request):
    """Création du profil de rencontre."""
    if hasattr(request.user, 'profil_rencontre'):
        return redirect('rencontres:decouverte')

    if request.method == 'POST':
        form = ProfilRencontreForm(request.POST, request.FILES)
        if form.is_valid():
            profil = form.save(commit=False)
            profil.user = request.user
            profil.save()
            profil.calculer_completion()
            messages.success(request, "Votre profil a été créé ! Bienvenue sur E-Shelle Love.")
            return redirect('rencontres:decouverte')
    else:
        # Pré-remplir avec les données du profil existant
        initial = {}
        if hasattr(request.user, 'profile'):
            p = request.user.profile
            initial['ville'] = p.ville
            initial['pays'] = p.pays
        form = ProfilRencontreForm(initial=initial)

    return render(request, 'rencontres/profile_edit.html', {
        'form': form,
        'titre': 'Créer mon profil',
        'est_creation': True,
    })


@profil_requis
def modifier_profil(request):
    """Modification du profil de rencontre."""
    profil = request.user.profil_rencontre

    if request.method == 'POST':
        form = ProfilRencontreForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            profil.calculer_completion()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('rencontres:detail_profil', pk=profil.pk)
    else:
        form = ProfilRencontreForm(instance=profil)

    return render(request, 'rencontres/profile_edit.html', {
        'form': form,
        'profil': profil,
        'titre': 'Modifier mon profil',
        'est_creation': False,
    })


@profil_requis
def detail_profil(request, pk):
    """Détail d'un profil de rencontre."""
    mon_profil = request.user.profil_rencontre

    if pk == mon_profil.pk:
        profil = mon_profil
        est_mon_profil = True
    else:
        profil = get_object_or_404(ProfilRencontre, pk=pk, est_actif=True)
        est_mon_profil = False

        # Vérifier les blocages
        if mon_profil.a_bloque(profil) or mon_profil.est_bloque_par(profil):
            raise Http404

        # Incrémenter les vues
        ProfilRencontre.objects.filter(pk=pk).update(
            vues_profil=profil.vues_profil + 1
        )

    # Statut du like
    a_like = False
    est_match = False
    if not est_mon_profil:
        a_like = Like.objects.filter(envoyeur=mon_profil, recepteur=profil).exists()
        est_match = Match.objects.filter(
            Q(profil_1=mon_profil, profil_2=profil) |
            Q(profil_1=profil, profil_2=mon_profil),
            est_actif=True
        ).exists()

    photos = profil.photos.filter(est_approuvee=True).order_by('ordre')
    notifs = get_stats_notifications(mon_profil)

    return render(request, 'rencontres/profile_detail.html', {
        'profil': profil,
        'est_mon_profil': est_mon_profil,
        'a_like': a_like,
        'est_match': est_match,
        'photos': photos,
        'notifs': notifs,
    })


@profil_requis
def gerer_photos(request):
    """Gérer les photos du profil."""
    profil = request.user.profil_rencontre
    photos_max = 12 if profil.est_premium else 6

    if request.method == 'POST':
        if 'supprimer' in request.POST:
            photo_id = request.POST.get('photo_id')
            PhotoProfil.objects.filter(pk=photo_id, profil=profil).delete()
            messages.success(request, "Photo supprimée.")
            return redirect('rencontres:gerer_photos')

        form = PhotoProfilForm(request.POST, request.FILES)
        if form.is_valid():
            nb_photos = profil.photos.count()
            if nb_photos >= photos_max:
                messages.error(
                    request,
                    f"Vous avez atteint la limite de {photos_max} photos. "
                    f"{'Passez en premium pour en ajouter plus.' if not profil.est_premium else ''}"
                )
            else:
                photo = form.save(commit=False)
                photo.profil = profil
                photo.ordre = nb_photos
                photo.save()
                # Mettre comme principale si c'est la première
                if nb_photos == 0 or form.cleaned_data.get('est_principale'):
                    profil.photo_principale = photo.image
                    profil.save(update_fields=['photo_principale'])
                messages.success(request, "Photo ajoutée avec succès.")
                profil.calculer_completion()
            return redirect('rencontres:gerer_photos')
    else:
        form = PhotoProfilForm()

    photos = profil.photos.filter(est_approuvee=True).order_by('ordre')
    return render(request, 'rencontres/gerer_photos.html', {
        'form': form,
        'photos': photos,
        'profil': profil,
        'photos_max': photos_max,
        'peut_ajouter': profil.photos.count() < photos_max,
    })


@profil_requis
def parametres_rencontre(request):
    """Paramètres de confidentialité et préférences."""
    profil = request.user.profil_rencontre

    if request.method == 'POST':
        profil.afficher_en_ligne = 'afficher_en_ligne' in request.POST
        profil.afficher_distance = 'afficher_distance' in request.POST
        profil.qui_peut_ecrire = request.POST.get('qui_peut_ecrire', 'tous')
        profil.save(update_fields=['afficher_en_ligne', 'afficher_distance', 'qui_peut_ecrire'])
        messages.success(request, "Paramètres sauvegardés.")
        return redirect('rencontres:parametres')

    return render(request, 'rencontres/parametres.html', {'profil': profil})


@profil_requis
def desactiver_compte_rencontre(request):
    """Désactiver (masquer) le compte de rencontre."""
    profil = request.user.profil_rencontre

    if request.method == 'POST':
        profil.est_actif = False
        profil.save(update_fields=['est_actif'])
        messages.success(request, "Votre profil de rencontre a été désactivé.")
        return redirect('rencontres:accueil')

    return render(request, 'rencontres/desactiver.html', {'profil': profil})
