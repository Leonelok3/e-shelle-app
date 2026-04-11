from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from rencontres.models import PlanPremiumRencontre, AbonnementRencontre, Like, Match
from rencontres.utils.notifications import get_stats_notifications
from rencontres.views.profile_views import profil_requis


@profil_requis
def page_premium(request):
    """Page de présentation des plans premium."""
    profil = request.user.profil_rencontre
    notifs = get_stats_notifications(profil)

    plans = PlanPremiumRencontre.objects.all().order_by('prix_mensuel')

    abonnement_actif = AbonnementRencontre.objects.filter(
        profil=profil, est_actif=True, date_fin__gt=timezone.now()
    ).select_related('plan').first()

    return render(request, 'rencontres/premium.html', {
        'profil': profil,
        'plans': plans,
        'abonnement_actif': abonnement_actif,
        'notifs': notifs,
    })


@profil_requis
def souscrire_premium(request, plan):
    """Souscription à un plan premium rencontre via Mobile Money."""
    profil = request.user.profil_rencontre
    plan_obj = get_object_or_404(PlanPremiumRencontre, nom=plan)

    if request.method == 'POST':
        periodicite = request.POST.get('periodicite', 'mensuel')
        methode     = request.POST.get('methode', 'mtn_momo')
        telephone   = request.POST.get('telephone', '')

        montant     = plan_obj.prix_xaf_mensuel if periodicite == 'mensuel' else plan_obj.prix_xaf_annuel
        duree_jours = 30 if periodicite == 'mensuel' else 365

        try:
            from payments.models import Transaction as PaymentTransaction
            tx = PaymentTransaction.objects.create(
                utilisateur=request.user,
                type_tx='abonnement',
                methode=methode,
                montant=montant,
                telephone=telephone,
                devise='XAF',
                metadata={
                    'plan_rencontre': plan,
                    'periodicite': periodicite,
                    'duree_jours': duree_jours,
                },
            )
            # TODO: Intégrer API MTN/Airtel — simulation pour l'instant
            tx.statut = 'succes'
            tx.save()

            # Activer l'abonnement immédiatement
            activer_abonnement_premium(profil, plan, duree_jours, str(tx.reference))

            messages.success(
                request,
                f"✅ Plan {plan_obj.get_nom_display()} activé ! "
                f"Votre profil est maintenant Premium pour {duree_jours} jours."
            )
            return redirect('rencontres:premium')

        except Exception as e:
            messages.error(request, f"Erreur lors du paiement : {e}")

    return render(request, 'rencontres/souscrire.html', {
        'plan':   plan_obj,
        'profil': profil,
    })


def activer_abonnement_premium(profil, plan_nom, duree_jours, payment_reference=''):
    """
    Appelé après confirmation de paiement pour activer l'abonnement.
    À connecter au webhook/signal de paiement.
    """
    plan = PlanPremiumRencontre.objects.get(nom=plan_nom)

    # Désactiver les anciens abonnements
    AbonnementRencontre.objects.filter(profil=profil, est_actif=True).update(est_actif=False)

    # Créer le nouvel abonnement
    abo = AbonnementRencontre.objects.create(
        profil=profil,
        plan=plan,
        date_fin=timezone.now() + timedelta(days=duree_jours),
        payment_reference=payment_reference
    )

    # Mettre à jour le statut premium du profil
    profil.est_premium = True
    profil.save(update_fields=['est_premium'])

    return abo


@profil_requis
def activer_boost(request):
    """Activer un boost de profil (premium seulement)."""
    profil = request.user.profil_rencontre

    if not profil.est_premium:
        messages.error(request, "Le boost de profil est réservé aux membres premium.")
        return redirect('rencontres:premium')

    if request.method == 'POST':
        # Logique de boost : stocker l'heure de fin de boost
        from django.utils import timezone
        boost_fin = timezone.now() + timedelta(minutes=30)
        request.session['boost_actif_jusqu'] = boost_fin.isoformat()
        messages.success(
            request,
            "Boost activé ! Votre profil sera mis en avant pendant 30 minutes."
        )
        return redirect('rencontres:decouverte')

    return render(request, 'rencontres/boost.html', {'profil': profil})


@profil_requis
def ajax_stats_profil(request):
    """Statistiques du profil (premium uniquement)."""
    profil = request.user.profil_rencontre

    if not profil.est_premium:
        return JsonResponse({'error': 'Premium requis'}, status=403)

    nb_likes = Like.objects.filter(recepteur=profil).count()
    nb_matchs = Match.objects.filter(
        __import__('django.db.models', fromlist=['Q']).Q(profil_1=profil) |
        __import__('django.db.models', fromlist=['Q']).Q(profil_2=profil)
    ).count()

    return JsonResponse({
        'vues_profil': profil.vues_profil,
        'nb_likes': nb_likes,
        'nb_matchs': nb_matchs,
        'taux_match': round((nb_matchs / nb_likes * 100) if nb_likes > 0 else 0, 1),
        'profil_complet': profil.profil_complet,
    })
