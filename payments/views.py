"""
payments/views.py — Vues paiement Mobile Money E-Shelle
Initiation paiement, webhook confirmation, historique.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
import json

from .models import Transaction
from boutique.models import Commande


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
