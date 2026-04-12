"""pharma/views.py — E-Shelle Pharma"""
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Min
from .models import (VillePharma, QuartierPharma, CategorieMedicament,
                     Medicament, Pharmacie, StockPharmacie, AvisPharmacie)

TAILLES_CHOICES = []  # unused here, kept for consistency


def _pharmacies_actives():
    return Pharmacie.objects.filter(is_active=True, abonnement_actif=True)


# ─── Accueil ──────────────────────────────────────────────────────────────────

def accueil(request):
    villes      = VillePharma.objects.filter(active=True)
    categories  = CategorieMedicament.objects.filter(active=True)
    pharmacies_vedette = _pharmacies_actives().filter(is_featured=True).select_related("ville", "quartier")[:6]
    medicaments_populaires = Medicament.objects.filter(actif=True).annotate(
        nb_dispo=Count("stocks", filter=Q(
            stocks__disponible=True,
            stocks__pharmacie__is_active=True,
            stocks__pharmacie__abonnement_actif=True,
        ))
    ).filter(nb_dispo__gt=0).order_by("-nb_dispo")[:12]

    stats = {
        "nb_pharmacies": _pharmacies_actives().count(),
        "nb_medicaments": Medicament.objects.filter(actif=True).count(),
        "nb_villes": villes.count(),
        "nb_stocks": StockPharmacie.objects.filter(disponible=True).count(),
    }

    return render(request, "pharma/accueil.html", {
        "villes": villes,
        "categories": categories,
        "pharmacies_vedette": pharmacies_vedette,
        "medicaments_populaires": medicaments_populaires,
        "stats": stats,
    })


# ─── Recherche médicament ─────────────────────────────────────────────────────

def recherche(request):
    q            = request.GET.get("q", "").strip()
    ville_slug   = request.GET.get("ville", "")
    cat_slug     = request.GET.get("cat", "")
    garde_only   = request.GET.get("garde", "")
    livraison    = request.GET.get("livraison", "")

    villes     = VillePharma.objects.filter(active=True)
    categories = CategorieMedicament.objects.filter(active=True)

    medicaments = Medicament.objects.filter(actif=True)
    if q:
        medicaments = medicaments.filter(nom__icontains=q)
    if cat_slug:
        medicaments = medicaments.filter(categorie__slug=cat_slug)

    # Pour chaque médicament, récupérer les pharmacies qui l'ont
    ville_active = None
    if ville_slug:
        try:
            ville_active = VillePharma.objects.get(slug=ville_slug)
        except VillePharma.DoesNotExist:
            pass

    # Annoter nb pharmacies dispo
    stocks_qs = StockPharmacie.objects.filter(
        disponible=True,
        pharmacie__is_active=True,
        pharmacie__abonnement_actif=True,
    )
    if ville_active:
        stocks_qs = stocks_qs.filter(pharmacie__ville=ville_active)
    if garde_only:
        stocks_qs = stocks_qs.filter(pharmacie__garde=True)
    if livraison:
        stocks_qs = stocks_qs.filter(pharmacie__livraison=True)

    medicaments = medicaments.annotate(
        nb_dispo=Count("stocks", filter=Q(
            stocks__disponible=True,
            stocks__pharmacie__is_active=True,
            stocks__pharmacie__abonnement_actif=True,
            **({} if not ville_active else {"stocks__pharmacie__ville": ville_active}),
        ))
    ).order_by("-nb_dispo", "nom")

    return render(request, "pharma/recherche.html", {
        "q": q,
        "villes": villes,
        "categories": categories,
        "medicaments": medicaments,
        "ville_slug": ville_slug,
        "ville_active": ville_active,
        "cat_slug": cat_slug,
        "garde_only": garde_only,
        "livraison": livraison,
        "nb_results": medicaments.count(),
    })


# ─── Détail médicament → pharmacies qui l'ont ────────────────────────────────

def detail_medicament(request, slug):
    medicament = get_object_or_404(Medicament, slug=slug, actif=True)
    ville_slug = request.GET.get("ville", "")
    garde_only = request.GET.get("garde", "")

    stocks = StockPharmacie.objects.filter(
        medicament=medicament,
        disponible=True,
        pharmacie__is_active=True,
        pharmacie__abonnement_actif=True,
    ).select_related("pharmacie", "pharmacie__ville", "pharmacie__quartier").order_by("prix")

    if ville_slug:
        stocks = stocks.filter(pharmacie__ville__slug=ville_slug)
    if garde_only:
        stocks = stocks.filter(pharmacie__garde=True)

    villes = VillePharma.objects.filter(active=True)
    medicaments_similaires = Medicament.objects.filter(
        actif=True, categorie=medicament.categorie
    ).exclude(pk=medicament.pk)[:6]

    return render(request, "pharma/detail_medicament.html", {
        "medicament": medicament,
        "stocks": stocks,
        "nb_results": stocks.count(),
        "villes": villes,
        "ville_slug": ville_slug,
        "garde_only": garde_only,
        "medicaments_similaires": medicaments_similaires,
    })


# ─── Catalogue pharmacies ─────────────────────────────────────────────────────

def catalogue(request):
    q           = request.GET.get("q", "").strip()
    ville_slug  = request.GET.get("ville", "")
    quartier_id = request.GET.get("quartier", "")
    garde_only  = request.GET.get("garde", "")
    livraison   = request.GET.get("livraison", "")

    villes = VillePharma.objects.filter(active=True)
    pharmacies = _pharmacies_actives().select_related("ville", "quartier")

    ville_active = None
    if ville_slug:
        try:
            ville_active = VillePharma.objects.get(slug=ville_slug)
            pharmacies = pharmacies.filter(ville=ville_active)
        except VillePharma.DoesNotExist:
            pass

    quartiers_list = []
    if ville_active:
        quartiers_list = QuartierPharma.objects.filter(ville=ville_active, active=True)

    if quartier_id:
        pharmacies = pharmacies.filter(quartier__pk=quartier_id)
    if garde_only:
        pharmacies = pharmacies.filter(garde=True)
    if livraison:
        pharmacies = pharmacies.filter(livraison=True)
    if q:
        pharmacies = pharmacies.filter(
            Q(nom__icontains=q) | Q(adresse__icontains=q) | Q(quartier__nom__icontains=q)
        )

    pharmacies = pharmacies.order_by("-is_featured", "-is_verified", "nom")

    return render(request, "pharma/catalogue.html", {
        "pharmacies": pharmacies,
        "villes": villes,
        "ville_active": ville_active,
        "ville_slug": ville_slug,
        "quartiers_list": quartiers_list,
        "quartier_id": quartier_id,
        "garde_only": garde_only,
        "livraison": livraison,
        "q": q,
        "nb_results": pharmacies.count(),
    })


# ─── Détail pharmacie ─────────────────────────────────────────────────────────

def detail_pharmacie(request, slug):
    pharmacie = get_object_or_404(Pharmacie, slug=slug, is_active=True, abonnement_actif=True)

    # Stock médicaments disponibles
    stocks = pharmacie.stocks.filter(disponible=True).select_related(
        "medicament", "medicament__categorie"
    ).order_by("medicament__categorie__nom", "medicament__nom")

    # Filtrer par catégorie
    cat_slug = request.GET.get("cat", "")
    if cat_slug:
        stocks = stocks.filter(medicament__categorie__slug=cat_slug)

    categories_dispo = CategorieMedicament.objects.filter(
        medicaments__stocks__pharmacie=pharmacie,
        medicaments__stocks__disponible=True,
    ).distinct()

    # Avis
    avis_list = pharmacie.avis.select_related("auteur").all()
    user_avis = None
    avis_error = ""

    if request.method == "POST" and request.user.is_authenticated:
        note = request.POST.get("note")
        commentaire = request.POST.get("commentaire", "").strip()
        if note and note.isdigit() and 1 <= int(note) <= 5:
            obj, created = AvisPharmacie.objects.get_or_create(
                pharmacie=pharmacie,
                auteur=request.user,
                defaults={"note": int(note), "commentaire": commentaire},
            )
            if not created:
                obj.note = int(note)
                obj.commentaire = commentaire
                obj.save()
        else:
            avis_error = "Veuillez sélectionner une note."

    if request.user.is_authenticated:
        user_avis = AvisPharmacie.objects.filter(
            pharmacie=pharmacie, auteur=request.user
        ).first()

    # Pharmacies similaires
    similaires = _pharmacies_actives().filter(
        ville=pharmacie.ville
    ).exclude(pk=pharmacie.pk).select_related("ville", "quartier")[:4]

    return render(request, "pharma/detail_pharmacie.html", {
        "pharmacie": pharmacie,
        "stocks": stocks,
        "categories_dispo": categories_dispo,
        "cat_slug": cat_slug,
        "avis_list": avis_list,
        "user_avis": user_avis,
        "avis_error": avis_error,
        "similaires": similaires,
    })
