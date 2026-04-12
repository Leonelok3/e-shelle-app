"""pressing/views.py — E-Shelle Pressing"""
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (VillePressing, QuartierPressing, CategoriePressing,
                     Pressing, ServicePressing, CommandePressing, AvisPressing)


def _actifs():
    return Pressing.objects.filter(is_active=True, abonnement_actif=True)


# ─── Accueil ──────────────────────────────────────────────────────────────────

def accueil(request):
    villes     = VillePressing.objects.filter(active=True)
    categories = CategoriePressing.objects.filter(active=True)
    vedettes   = _actifs().filter(is_featured=True).select_related("ville", "quartier").prefetch_related("categories")[:6]
    recents    = _actifs().order_by("-created_at").select_related("ville", "quartier")[:4]

    stats = {
        "nb_pressings": _actifs().count(),
        "nb_villes": villes.count(),
        "nb_commandes": CommandePressing.objects.count(),
    }

    return render(request, "pressing/accueil.html", {
        "villes": villes,
        "categories": categories,
        "vedettes": vedettes,
        "recents": recents,
        "stats": stats,
    })


# ─── Catalogue ────────────────────────────────────────────────────────────────

def catalogue(request):
    q            = request.GET.get("q", "").strip()
    ville_slug   = request.GET.get("ville", "")
    quartier_id  = request.GET.get("quartier", "")
    cat_slug     = request.GET.get("cat", "")
    express_only = request.GET.get("express", "")
    collecte     = request.GET.get("collecte", "")
    livraison    = request.GET.get("livraison", "")

    villes     = VillePressing.objects.filter(active=True)
    categories = CategoriePressing.objects.filter(active=True)
    pressings  = _actifs().select_related("ville", "quartier").prefetch_related("categories")

    ville_active = None
    if ville_slug:
        try:
            ville_active = VillePressing.objects.get(slug=ville_slug)
            pressings = pressings.filter(ville=ville_active)
        except VillePressing.DoesNotExist:
            pass

    quartiers_list = []
    if ville_active:
        quartiers_list = QuartierPressing.objects.filter(ville=ville_active, active=True)

    if quartier_id:
        pressings = pressings.filter(quartier__pk=quartier_id)
    if cat_slug:
        pressings = pressings.filter(categories__slug=cat_slug)
    if express_only:
        pressings = pressings.filter(express=True)
    if collecte:
        pressings = pressings.filter(collecte_domicile=True)
    if livraison:
        pressings = pressings.filter(livraison_domicile=True)
    if q:
        pressings = pressings.filter(
            Q(nom__icontains=q) | Q(adresse__icontains=q) |
            Q(quartier__nom__icontains=q) | Q(zone_livraison__icontains=q)
        )

    pressings = pressings.distinct().order_by("-is_featured", "-is_verified", "nom")

    return render(request, "pressing/catalogue.html", {
        "pressings": pressings,
        "villes": villes,
        "categories": categories,
        "ville_active": ville_active,
        "ville_slug": ville_slug,
        "quartiers_list": quartiers_list,
        "quartier_id": quartier_id,
        "cat_slug": cat_slug,
        "express_only": express_only,
        "collecte": collecte,
        "livraison": livraison,
        "q": q,
        "nb_results": pressings.count(),
    })


# ─── Détail pressing ──────────────────────────────────────────────────────────

def detail(request, slug):
    pressing = get_object_or_404(Pressing, slug=slug, is_active=True, abonnement_actif=True)

    # Compteur de vues
    Pressing.objects.filter(pk=pressing.pk).update(nb_vues=pressing.nb_vues + 1)

    # Services groupés par catégorie
    services = pressing.services.filter(disponible=True).select_related("categorie").order_by("categorie__ordre", "ordre")
    categories_services = {}
    for svc in services:
        cat_nom = svc.categorie.nom if svc.categorie else "Autres"
        cat_icone = svc.categorie.icone if svc.categorie else "🧺"
        key = (cat_nom, cat_icone)
        categories_services.setdefault(key, []).append(svc)

    # Avis
    avis_list  = pressing.avis.select_related("auteur").all()
    user_avis  = None
    avis_error = ""

    if request.method == "POST" and "note" in request.POST:
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next={request.path}")
        note = request.POST.get("note", "")
        commentaire = request.POST.get("commentaire", "").strip()
        if note.isdigit() and 1 <= int(note) <= 5:
            obj, created = AvisPressing.objects.get_or_create(
                pressing=pressing, auteur=request.user,
                defaults={"note": int(note), "commentaire": commentaire},
            )
            if not created:
                obj.note = int(note)
                obj.commentaire = commentaire
                obj.save()
            messages.success(request, "Votre avis a été enregistré.")
            return redirect("pressing:detail", slug=slug)
        else:
            avis_error = "Veuillez sélectionner une note entre 1 et 5."

    if request.user.is_authenticated:
        user_avis = AvisPressing.objects.filter(pressing=pressing, auteur=request.user).first()

    similaires = _actifs().filter(ville=pressing.ville).exclude(pk=pressing.pk).select_related("ville", "quartier")[:4]

    return render(request, "pressing/detail.html", {
        "pressing": pressing,
        "categories_services": categories_services,
        "avis_list": avis_list,
        "user_avis": user_avis,
        "avis_error": avis_error,
        "similaires": similaires,
        "services_json": json.dumps([
            {"id": s.pk, "nom": s.nom, "icone": s.icone,
             "prix": s.prix, "unite": s.get_unite_display()}
            for s in services
        ], ensure_ascii=False),
    })


# ─── Commander ────────────────────────────────────────────────────────────────

def commander(request, slug):
    pressing = get_object_or_404(Pressing, slug=slug, is_active=True, abonnement_actif=True)
    services = pressing.services.filter(disponible=True).select_related("categorie").order_by("categorie__ordre", "ordre")

    if request.method == "POST":
        articles_raw = request.POST.get("articles_json", "[]")
        try:
            articles = json.loads(articles_raw)
        except (json.JSONDecodeError, ValueError):
            articles = []

        if not articles:
            messages.error(request, "Veuillez sélectionner au moins un article.")
            return redirect("pressing:commander", slug=slug)

        montant_total = sum(a.get("prix_unit", 0) * a.get("qte", 1) for a in articles)

        nom_client   = request.POST.get("nom_client", "").strip()
        tel_client   = request.POST.get("tel_client", "").strip()
        mode         = request.POST.get("mode", "depot")
        adresse      = request.POST.get("adresse_collecte", "").strip()
        notes        = request.POST.get("notes", "").strip()
        date_collecte_str = request.POST.get("date_collecte", "")

        if not tel_client:
            messages.error(request, "Veuillez renseigner votre numéro de téléphone.")
            return redirect("pressing:commander", slug=slug)

        from datetime import datetime
        date_collecte = None
        if date_collecte_str:
            try:
                date_collecte = datetime.strptime(date_collecte_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        commande = CommandePressing.objects.create(
            pressing=pressing,
            client=request.user if request.user.is_authenticated else None,
            nom_client=nom_client or (request.user.get_full_name() if request.user.is_authenticated else ""),
            tel_client=tel_client,
            mode=mode,
            adresse_collecte=adresse,
            articles=articles,
            notes=notes,
            montant_total=montant_total,
            date_collecte=date_collecte,
            statut="en_attente",
        )

        return redirect("pressing:confirmation", pk=commande.pk)

    return render(request, "pressing/commander.html", {
        "pressing": pressing,
        "services": services,
        "categories_services": _group_services(services),
    })


def _group_services(services):
    groups = {}
    for svc in services:
        cat_nom = svc.categorie.nom if svc.categorie else "Autres"
        cat_icone = svc.categorie.icone if svc.categorie else "🧺"
        groups.setdefault((cat_nom, cat_icone), []).append(svc)
    return groups


# ─── Confirmation ─────────────────────────────────────────────────────────────

def confirmation(request, pk):
    commande = get_object_or_404(CommandePressing, pk=pk)
    # Enrichit chaque article avec son sous-total pour affichage dans le template
    articles_enrichis = []
    for art in commande.articles:
        art_copy = dict(art)
        art_copy["sous_total"] = art_copy.get("prix_unit", 0) * art_copy.get("qte", 1)
        articles_enrichis.append(art_copy)
    return render(request, "pressing/confirmation.html", {
        "commande": commande,
        "articles_enrichis": articles_enrichis,
    })


# ─── Dashboard pressing (propriétaire) ───────────────────────────────────────

@login_required
def dashboard(request):
    pressings = Pressing.objects.filter(gerant=request.user)
    if not pressings.exists():
        messages.info(request, "Vous n'avez pas encore de pressing enregistré.")
        return redirect("pressing:accueil")

    pressing = pressings.first()
    commandes = CommandePressing.objects.filter(pressing=pressing).order_by("-created_at")

    statut_filter = request.GET.get("statut", "")
    if statut_filter:
        commandes = commandes.filter(statut=statut_filter)

    stats = {
        "total": commandes.count(),
        "en_attente": commandes.filter(statut="en_attente").count(),
        "en_cours": commandes.filter(statut__in=["confirme", "en_cours"]).count(),
        "pret": commandes.filter(statut="pret").count(),
        "ca": commandes.filter(statut="livre").aggregate(s=Sum("montant_total"))["s"] or 0,
    }

    return render(request, "pressing/dashboard.html", {
        "pressing": pressing,
        "commandes": commandes[:50],
        "stats": stats,
        "statut_filter": statut_filter,
        "statut_choices": CommandePressing.STATUT_CHOICES,
    })


@login_required
@require_POST
def update_statut(request, pk):
    commande = get_object_or_404(CommandePressing, pk=pk, pressing__gerant=request.user)
    nouveau_statut = request.POST.get("statut", "")
    statuts_valides = [s[0] for s in CommandePressing.STATUT_CHOICES]
    if nouveau_statut in statuts_valides:
        commande.statut = nouveau_statut
        commande.save(update_fields=["statut", "updated_at"])
        messages.success(request, f"Commande #{commande.pk} mise à jour : {commande.get_statut_display()}")
    return redirect("pressing:dashboard")
