"""
api/views.py — API REST E-Shelle (DRF)
Endpoints JSON pour les opérations AJAX du frontend.
"""
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_GET


@require_GET
def search(request):
    """Recherche globale : formations + produits."""
    q = request.GET.get("q", "").strip()
    results = []

    if len(q) >= 2:
        from formations.models import Formation
        from boutique.models import Produit

        formations = Formation.objects.filter(
            is_published=True
        ).filter(Q(titre__icontains=q) | Q(description__icontains=q))[:5]

        produits = Produit.objects.filter(
            is_published=True
        ).filter(Q(titre__icontains=q) | Q(description__icontains=q))[:5]

        for f in formations:
            results.append({
                "type":  "Formation",
                "title": f.titre,
                "url":   f"/formations/{f.slug}/",
            })
        for p in produits:
            results.append({
                "type":  "Produit",
                "title": p.titre,
                "url":   f"/boutique/{p.slug}/",
            })

    return JsonResponse({"results": results, "q": q})


@require_GET
def notifications_count(request):
    """Nombre de notifications non lues pour l'utilisateur connecté."""
    if not request.user.is_authenticated:
        return JsonResponse({"count": 0})

    from dashboard.models import Notification
    count = Notification.objects.filter(
        destinataire=request.user, lue=False
    ).count()
    return JsonResponse({"count": count})
