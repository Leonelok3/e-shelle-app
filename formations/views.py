"""
formations/views.py — Vues du module Formation E-Shelle
Catalogue, détail formation, lecteur de cours, dashboard apprenant.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

from .models import (
    Categorie, Formation, Chapitre, Lecon, Inscription,
    Progression, AvisFormation, Certificat, Quiz, ResultatQuiz
)


def catalogue(request):
    """Catalogue des formations avec filtres."""
    formations = Formation.objects.filter(is_published=True).select_related("categorie", "formateur")
    categories = Categorie.objects.filter(active=True)

    # Filtres
    cat_slug  = request.GET.get("categorie", "")
    niveau    = request.GET.get("niveau", "")
    langue    = request.GET.get("langue", "")
    gratuit   = request.GET.get("gratuit", "")
    recherche = request.GET.get("q", "")

    if cat_slug:
        formations = formations.filter(categorie__slug=cat_slug)
    if niveau:
        formations = formations.filter(niveau=niveau)
    if langue:
        formations = formations.filter(langue=langue)
    if gratuit:
        formations = formations.filter(prix=0)
    if recherche:
        formations = formations.filter(
            Q(titre__icontains=recherche) | Q(description__icontains=recherche)
        )

    # Tri
    tri = request.GET.get("tri", "-created_at")
    formations = formations.order_by(tri)

    classes_math = [
        ("3eme",   "3ème"),
        ("2nde",   "2nde"),
        ("1ere_a", "1ère A"),
        ("1ere_c", "1ère C"),
        ("1ere_d", "1ère D"),
        ("tle_a",  "Tle A"),
        ("tle_c",  "Tle C"),
        ("tle_d",  "Tle D"),
    ]

    context = {
        "formations":   formations,
        "categories":   categories,
        "cat_slug":     cat_slug,
        "niveau":       niveau,
        "langue":       langue,
        "recherche":    recherche,
        "niveaux":      Formation.NIVEAUX,
        "langues":      Formation.LANGUES,
        "classes_math": classes_math,
    }
    return render(request, "formations/catalogue.html", context)


def detail(request, slug):
    """Page détail d'une formation."""
    formation = get_object_or_404(Formation, slug=slug, is_published=True)
    chapitres = formation.chapitres.prefetch_related("lecons").order_by("ordre")
    avis      = formation.avis.select_related("utilisateur").order_by("-created_at")[:6]

    # Vérifier si l'utilisateur est inscrit
    inscrit = False
    progression_pct = 0
    if request.user.is_authenticated:
        inscription = Inscription.objects.filter(
            utilisateur=request.user, formation=formation
        ).first()
        if inscription:
            inscrit = True
            progression_pct = inscription.progression_pct

    formations_similaires = Formation.objects.filter(
        categorie=formation.categorie, is_published=True
    ).exclude(pk=formation.pk)[:3]

    context = {
        "formation":  formation,
        "chapitres":  chapitres,
        "avis":       avis,
        "inscrit":    inscrit,
        "progression_pct": progression_pct,
        "formations_similaires": formations_similaires,
    }
    return render(request, "formations/detail.html", context)


@login_required
def lecteur(request, formation_slug, lecon_id):
    """Lecteur de cours — affiche une leçon et sa progression."""
    formation = get_object_or_404(Formation, slug=formation_slug, is_published=True)
    lecon     = get_object_or_404(Lecon, pk=lecon_id, chapitre__formation=formation)

    # Vérifier l'accès
    if not lecon.is_free:
        inscription = Inscription.objects.filter(
            utilisateur=request.user, formation=formation
        ).first()
        if not inscription and not request.user.is_staff:
            return redirect("formations:detail", slug=formation_slug)

    # Toutes les leçons (pour la sidebar)
    lecons_all = Lecon.objects.filter(
        chapitre__formation=formation, is_published=True
    ).select_related("chapitre").order_by("chapitre__ordre", "ordre")

    # Progression existante
    progression, _ = Progression.objects.get_or_create(
        utilisateur=request.user, lecon=lecon
    )

    # Marquage comme terminée
    if request.method == "POST" and "complete" in request.POST:
        progression.completee = True
        progression.date_completion = timezone.now()
        progression.save()
        _update_inscription_progress(request.user, formation)
        return redirect("formations:lecteur", formation_slug=formation_slug, lecon_id=lecon_id)

    # Navigation prev/next
    lecons_list = list(lecons_all)
    idx         = next((i for i, l in enumerate(lecons_list) if l.pk == lecon.pk), 0)
    lecon_prev  = lecons_list[idx - 1] if idx > 0 else None
    lecon_next  = lecons_list[idx + 1] if idx < len(lecons_list) - 1 else None

    # IDs des leçons terminées par l'utilisateur
    completees = set(Progression.objects.filter(
        utilisateur=request.user,
        lecon__chapitre__formation=formation,
        completee=True
    ).values_list("lecon_id", flat=True))

    context = {
        "formation":   formation,
        "lecon":       lecon,
        "lecons_all":  lecons_all,
        "lecon_prev":  lecon_prev,
        "lecon_next":  lecon_next,
        "progression": progression,
        "completees":  completees,
    }
    return render(request, "formations/lecteur.html", context)


def _update_inscription_progress(user, formation):
    """Met à jour le % de progression global d'une inscription."""
    inscription = Inscription.objects.filter(utilisateur=user, formation=formation).first()
    if not inscription:
        return
    nb_total = Lecon.objects.filter(
        chapitre__formation=formation, is_published=True
    ).count()
    if nb_total == 0:
        return
    nb_completees = Progression.objects.filter(
        utilisateur=user,
        lecon__chapitre__formation=formation,
        completee=True
    ).count()
    inscription.progression_pct = int(nb_completees / nb_total * 100)
    if inscription.progression_pct >= 100:
        inscription.termine = True
        inscription.date_fin = timezone.now()
    inscription.save()


@login_required
def mon_dashboard(request):
    """Dashboard de l'apprenant : inscriptions, progressions, badges."""
    inscriptions = Inscription.objects.filter(
        utilisateur=request.user
    ).select_related("formation").order_by("-date_inscription")

    certificats = Certificat.objects.filter(
        utilisateur=request.user
    ).select_related("formation").order_by("-date_obtenu")

    resultats = ResultatQuiz.objects.filter(
        utilisateur=request.user
    ).select_related("quiz").order_by("-created_at")[:10]

    context = {
        "inscriptions": inscriptions,
        "certificats":  certificats,
        "resultats":    resultats,
    }
    return render(request, "formations/dashboard_apprenant.html", context)


@login_required
def inscrire(request, slug):
    """Inscrire l'utilisateur à une formation (gratuite ou après paiement)."""
    formation = get_object_or_404(Formation, slug=slug, is_published=True)

    if formation.prix > 0:
        return redirect("payments:payer_formation", formation_id=formation.pk)

    # Formation gratuite — inscription directe
    inscription, created = Inscription.objects.get_or_create(
        utilisateur=request.user, formation=formation
    )
    if created:
        formation.nb_inscrits += 1
        formation.save(update_fields=["nb_inscrits"])

    return redirect("formations:lecteur", formation_slug=slug,
                    lecon_id=_premiere_lecon(formation))


def _premiere_lecon(formation):
    """Retourne l'ID de la première leçon publiée."""
    lecon = Lecon.objects.filter(
        chapitre__formation=formation, is_published=True
    ).order_by("chapitre__ordre", "ordre").first()
    return lecon.pk if lecon else 0
