"""
payments/views.py — Vues paiement Mobile Money E-Shelle
Initiation paiement, webhook confirmation, historique, packs premium marketplace.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
import json

from .models import Transaction
from boutique.models import Commande

# ─── Définitions des plans et boosts ─────────────────────────────

PLANS_PREMIUM = {
    "starter": {
        "nom": "Starter", "emoji": "⭐",
        "prix": 2000, "duree_jours": 30,
        "couleur": "#4CAF50", "populaire": False,
        "features": [
            "30 jours Premium",
            "Annonces / biens illimités",
            "Badge Premium visible",
            "Priorité dans les résultats",
        ],
    },
    "pro": {
        "nom": "Pro", "emoji": "🚀",
        "prix": 5000, "duree_jours": 90,
        "couleur": "#4FC3F7", "populaire": True,
        "features": [
            "90 jours Premium",
            "Annonces / biens illimités",
            "Badge Pro + profil mis en avant",
            "Statistiques de base",
            "Support prioritaire",
        ],
    },
    "expert": {
        "nom": "Expert", "emoji": "💎",
        "prix": 15000, "duree_jours": 365,
        "couleur": "#FFD700", "populaire": False,
        "features": [
            "1 an Premium",
            "Tout illimité",
            "Mise en avant permanente sur l'accueil",
            "Statistiques avancées",
            "Badge Expert animé",
            "Support WhatsApp dédié",
        ],
    },
}

BOOSTS_ANNONCE = {
    "REMONTEE_TOP":      {"nom": "Remontée en tête",  "prix": 500,  "duree_jours": 1,  "emoji": "⬆️",  "desc": "Revient en tête de liste pour 24h"},
    "MISE_EN_AVANT_7J":  {"nom": "Mise en avant 7j",  "prix": 1000, "duree_jours": 7,  "emoji": "🌟", "desc": "Encadré doré dans les résultats 7 jours"},
    "MISE_EN_AVANT_30J": {"nom": "Mise en avant 30j", "prix": 3500, "duree_jours": 30, "emoji": "🔥", "desc": "Encadré doré dans les résultats 30 jours"},
    "BADGE_URGENT":      {"nom": "Badge Urgent 7j",   "prix": 800,  "duree_jours": 7,  "emoji": "🔴", "desc": "Badge rouge URGENT visible 7 jours"},
    "PACK_COMPLET":      {"nom": "Pack Complet 30j",  "prix": 5000, "duree_jours": 30, "emoji": "💎", "desc": "Mise en avant + Urgent + Remontée pendant 30 jours"},
}

MODULES_LABEL = {
    "annonces": "Annonces Cam",
    "immo":     "Immobilier",
    "auto":     "Auto Cameroun",
    "agro":     "E-Shelle Agro",
}

MODULES_ICON = {
    "annonces": "📋",
    "immo":     "🏠",
    "auto":     "🚗",
    "agro":     "🌿",
}


def _activer_premium_module(user, module, plan_slug):
    """Active le compte premium sur le bon profil selon le module."""
    from datetime import timedelta
    duree = PLANS_PREMIUM[plan_slug]["duree_jours"]
    expiry = timezone.now().date() + timedelta(days=duree)

    if module == "annonces":
        from annonces_cam.models import ProfilVendeur, TypeCompteVendeur
        profil, _ = ProfilVendeur.objects.get_or_create(user=user)
        if profil.est_premium and profil.date_expiration_premium:
            expiry = profil.date_expiration_premium + timedelta(days=duree)
        profil.compte_type = TypeCompteVendeur.PREMIUM
        profil.date_expiration_premium = expiry
        profil.save(update_fields=["compte_type", "date_expiration_premium"])

    elif module == "immo":
        from immobilier_cameroun.models import ProfilImmo, TypeCompte
        profil, _ = ProfilImmo.objects.get_or_create(user=user)
        if profil.est_premium_actif and profil.date_expiration_premium:
            expiry = profil.date_expiration_premium + timedelta(days=duree)
        profil.compte_type = TypeCompte.PREMIUM
        profil.date_expiration_premium = expiry
        profil.save(update_fields=["compte_type", "date_expiration_premium"])

    elif module == "auto":
        from auto_cameroun.models import ProfilAuto, TypeCompteAuto
        profil, _ = ProfilAuto.objects.get_or_create(user=user)
        if profil.est_premium and profil.date_expiration_premium:
            expiry = profil.date_expiration_premium + timedelta(days=duree)
        profil.compte_type = TypeCompteAuto.PREMIUM
        profil.date_expiration_premium = expiry
        profil.save(update_fields=["compte_type", "date_expiration_premium"])

    elif module == "agro":
        from agro.models import ActeurAgro
        agro_map = {"starter": "silver", "pro": "gold", "expert": "platinum"}
        try:
            acteur = ActeurAgro.objects.get(user=user)
            acteur.plan_premium = agro_map.get(plan_slug, "silver")
            acteur.plan_expiry = expiry
            acteur.est_premium = True
            acteur.save(update_fields=["plan_premium", "plan_expiry", "est_premium"])
        except ActeurAgro.DoesNotExist:
            pass


@login_required
def initier(request, commande_id):
    """Page d'initiation du paiement Mobile Money."""
    commande = get_object_or_404(Commande, pk=commande_id, utilisateur=request.user)

    if request.method == "POST":
        methode   = request.POST.get("methode", "mtn_momo")
        telephone = request.POST.get("telephone", "")

        tx = Transaction.objects.create(
            utilisateur=request.user,
            type_tx="achat_produit",
            methode=methode,
            montant=commande.montant_total,
            telephone=telephone,
            commande=commande,
        )
        # TODO: Intégrer l'API MTN/Airtel ici
        # Pour l'instant, simulation : on passe directement en "succes"
        tx.statut = "succes"
        tx.save()

        commande.statut = "payee"
        commande.save(update_fields=["statut"])

        # Créer les liens de téléchargement pour chaque produit digital
        from boutique.models import Telechargement
        from datetime import timedelta
        from django.utils import timezone

        for ligne in commande.lignes.all():
            if ligne.produit.fichier or ligne.produit.url_externe:
                Telechargement.objects.create(
                    utilisateur=request.user,
                    produit=ligne.produit,
                    commande=commande,
                    expire_at=timezone.now() + timedelta(days=30),
                )
                ligne.produit.nb_ventes += 1
                ligne.produit.save(update_fields=["nb_ventes"])

        messages.success(request, "Paiement confirmé ! Vos fichiers sont prêts à télécharger.")
        return redirect("payments:confirmation", tx_id=tx.pk)

    context = {"commande": commande}
    return render(request, "payments/initier.html", context)


@login_required
def confirmation(request, tx_id):
    """Page de confirmation après paiement."""
    tx = get_object_or_404(Transaction, pk=tx_id, utilisateur=request.user)
    from boutique.models import Telechargement
    telechargements = Telechargement.objects.filter(
        commande=tx.commande
    ) if tx.commande else []

    return render(request, "payments/confirmation.html", {
        "transaction": tx,
        "telechargements": telechargements,
    })


@login_required
def historique(request):
    """Historique des transactions de l'utilisateur."""
    transactions = Transaction.objects.filter(
        utilisateur=request.user
    ).order_by("-created_at")
    return render(request, "payments/historique.html", {"transactions": transactions})


@csrf_exempt
def webhook(request):
    """Webhook pour les confirmations de paiement Mobile Money (MTN / Airtel)."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        ref  = data.get("reference", "")
        tx   = Transaction.objects.filter(ref_operateur=ref).first()

        if tx:
            statut = data.get("status", "")
            if statut in ("SUCCESS", "SUCCESSFUL"):
                tx.statut = "succes"
            elif statut in ("FAILED", "CANCELLED"):
                tx.statut = "echec"
            tx.save(update_fields=["statut"])

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"ok": True})


@login_required
def payer_formation(request, formation_id):
    """Paiement d'une formation payante via Mobile Money."""
    from formations.models import Formation, Inscription

    formation = get_object_or_404(Formation, pk=formation_id, is_published=True)

    # Déjà inscrit ?
    if Inscription.objects.filter(utilisateur=request.user, formation=formation).exists():
        messages.info(request, "Vous êtes déjà inscrit à cette formation.")
        return redirect("formations:detail", slug=formation.slug)

    if request.method == "POST":
        methode   = request.POST.get("methode", "mtn_momo")
        telephone = request.POST.get("telephone", "")

        tx = Transaction.objects.create(
            utilisateur=request.user,
            type_tx="achat_cours",
            methode=methode,
            montant=formation.prix,
            telephone=telephone,
            metadata={"formation_id": formation.pk, "formation_titre": formation.titre},
        )
        # TODO: Intégrer API MTN/Airtel — pour l'instant simulation
        tx.statut = "succes"
        tx.save()

        # Créer l'inscription
        _, created = Inscription.objects.get_or_create(
            utilisateur=request.user, formation=formation
        )
        if created:
            formation.nb_inscrits += 1
            formation.save(update_fields=["nb_inscrits"])

        messages.success(request, f"Paiement confirmé ! Vous êtes inscrit à « {formation.titre} ».")
        return redirect("formations:detail", slug=formation.slug)

    return render(request, "payments/payer_formation.html", {"formation": formation})


# ─── PACKS PREMIUM MARKETPLACE ───────────────────────────────────

@login_required
def premium_marketplace(request, module):
    """Page de choix du pack premium pour un module marketplace."""
    if module not in MODULES_LABEL:
        messages.error(request, "Module invalide.")
        return redirect("home")
    return render(request, "payments/premium_marketplace.html", {
        "module":       module,
        "module_label": MODULES_LABEL[module],
        "module_icon":  MODULES_ICON[module],
        "plans":        PLANS_PREMIUM,
    })


@login_required
def payer_premium(request, module, plan_slug):
    """Paiement du pack premium via Mobile Money + activation immédiate."""
    if module not in MODULES_LABEL or plan_slug not in PLANS_PREMIUM:
        messages.error(request, "Paramètres invalides.")
        return redirect("home")

    plan = PLANS_PREMIUM[plan_slug]

    if request.method == "POST":
        methode   = request.POST.get("methode", "mtn_momo")
        telephone = request.POST.get("telephone", "")

        tx = Transaction.objects.create(
            utilisateur=request.user,
            type_tx="premium_marketplac",
            methode=methode,
            montant=plan["prix"],
            telephone=telephone,
            metadata={
                "module":      module,
                "plan":        plan_slug,
                "plan_nom":    plan["nom"],
                "duree_jours": plan["duree_jours"],
            },
        )
        # TODO: Intégrer API MTN/Airtel — simulation
        tx.statut = "succes"
        tx.save()

        _activer_premium_module(request.user, module, plan_slug)

        messages.success(
            request,
            f"✅ Pack {plan['nom']} activé ! Votre compte {MODULES_LABEL[module]} est maintenant Premium pour {plan['duree_jours']} jours."
        )
        return redirect("payments:confirmation_premium", tx_id=tx.pk)

    return render(request, "payments/payer_premium.html", {
        "module":       module,
        "module_label": MODULES_LABEL[module],
        "module_icon":  MODULES_ICON[module],
        "plan":         plan,
        "plan_slug":    plan_slug,
    })


@login_required
def confirmation_premium(request, tx_id):
    """Confirmation après achat d'un pack premium."""
    tx = get_object_or_404(Transaction, pk=tx_id, utilisateur=request.user)
    module = (tx.metadata or {}).get("module", "")
    retour_urls = {
        "annonces": "/annonces/compte/mes-annonces/",
        "immo":     "/immobilier/compte/mes-biens/",
        "auto":     "/auto/compte/mes-vehicules/",
        "agro":     "/agro/dashboard/",
    }
    return render(request, "payments/confirmation_premium.html", {
        "transaction":  tx,
        "module":       module,
        "module_label": MODULES_LABEL.get(module, ""),
        "module_icon":  MODULES_ICON.get(module, ""),
        "retour_url":   retour_urls.get(module, "/"),
    })


@login_required
def booster_annonce(request, annonce_id, type_boost):
    """Paiement pour booster une annonce individuelle."""
    from annonces_cam.models import Annonce, BoostAnnonce
    from datetime import timedelta

    annonce = get_object_or_404(Annonce, pk=annonce_id, vendeur=request.user)

    if type_boost not in BOOSTS_ANNONCE:
        messages.error(request, "Type de boost invalide.")
        return redirect("annonces:mes_annonces")

    boost_info = BOOSTS_ANNONCE[type_boost]

    if request.method == "POST":
        methode   = request.POST.get("methode", "mtn_momo")
        telephone = request.POST.get("telephone", "")

        tx = Transaction.objects.create(
            utilisateur=request.user,
            type_tx="boost_annonce",
            methode=methode,
            montant=boost_info["prix"],
            telephone=telephone,
            metadata={
                "annonce_id":    annonce.pk,
                "annonce_titre": annonce.titre,
                "type_boost":    type_boost,
            },
        )
        tx.statut = "succes"
        tx.save()

        date_fin = timezone.now() + timedelta(days=boost_info["duree_jours"])
        BoostAnnonce.objects.create(
            annonce=annonce,
            type_boost=type_boost,
            prix_paye=boost_info["prix"],
            date_fin=date_fin,
            est_actif=True,
            reference_paiement=str(tx.pk),
        )

        # Mettre à jour les flags visibilité
        update_fields = []
        if type_boost in ("MISE_EN_AVANT_7J", "MISE_EN_AVANT_30J", "PACK_COMPLET"):
            annonce.est_mise_en_avant = True
            update_fields.append("est_mise_en_avant")
        if type_boost in ("BADGE_URGENT", "PACK_COMPLET"):
            annonce.est_urgente = True
            update_fields.append("est_urgente")
        if update_fields:
            annonce.save(update_fields=update_fields)

        messages.success(request, f"✅ {boost_info['emoji']} {boost_info['nom']} activé sur « {annonce.titre[:40]} » !")
        return redirect("annonces:detail_annonce", slug=annonce.slug)

    return render(request, "payments/booster_annonce.html", {
        "annonce":     annonce,
        "boost_info":  boost_info,
        "type_boost":  type_boost,
        "tous_boosts": BOOSTS_ANNONCE,
    })
