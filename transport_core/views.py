from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DemandeTrajetForm, TrajetForm
from .models import DemandeTrajet, Trajet, VilleTransport


def accueil(request):
    base_trajets = Trajet.objects.filter(
        is_active=True,
        statut=Trajet.Statut.OUVERT,
        date_depart__gte=timezone.localdate(),
    ).select_related("depart", "arrivee")
    featured = base_trajets.filter(is_featured=True)[:4]
    trajets = base_trajets[:8]
    context = {
        "trajets": trajets,
        "featured": featured,
        "villes": VilleTransport.objects.filter(active=True)[:12],
        "nb_trajets": Trajet.objects.filter(is_active=True, statut=Trajet.Statut.OUVERT, date_depart__gte=timezone.localdate()).count(),
        "nb_villes": VilleTransport.objects.filter(active=True).count(),
    }
    return render(request, "transport_core/accueil.html", context)


def catalogue(request):
    trajets = Trajet.objects.filter(is_active=True, date_depart__gte=timezone.localdate()).select_related("depart", "arrivee")
    depart = request.GET.get("depart", "")
    arrivee = request.GET.get("arrivee", "")
    date = request.GET.get("date", "")
    type_trajet = request.GET.get("type", "")
    q = request.GET.get("q", "").strip()

    if depart:
        trajets = trajets.filter(depart__slug=depart)
    if arrivee:
        trajets = trajets.filter(arrivee__slug=arrivee)
    if date:
        trajets = trajets.filter(date_depart=date)
    if type_trajet:
        trajets = trajets.filter(type_trajet=type_trajet)
    if q:
        trajets = trajets.filter(Q(lieu_depart__icontains=q) | Q(lieu_arrivee__icontains=q) | Q(conducteur_nom__icontains=q))

    context = {
        "trajets": trajets,
        "villes": VilleTransport.objects.filter(active=True),
        "depart": depart,
        "arrivee": arrivee,
        "date": date,
        "type_trajet": type_trajet,
        "types": Trajet.TypeTrajet.choices,
        "q": q,
        "nb_results": trajets.count(),
    }
    return render(request, "transport_core/catalogue.html", context)


def detail(request, slug):
    trajet = get_object_or_404(Trajet.objects.select_related("depart", "arrivee"), slug=slug, is_active=True)
    Trajet.objects.filter(pk=trajet.pk).update(vues=trajet.vues + 1)
    similaires = Trajet.objects.filter(
        is_active=True,
        depart=trajet.depart,
        arrivee=trajet.arrivee,
        date_depart__gte=timezone.localdate(),
    ).exclude(pk=trajet.pk).select_related("depart", "arrivee")[:4]
    return render(request, "transport_core/detail.html", {"trajet": trajet, "similaires": similaires})


def publier(request):
    if request.method == "POST":
        form = TrajetForm(request.POST)
        if form.is_valid():
            trajet = form.save(commit=False)
            if request.user.is_authenticated:
                trajet.auteur = request.user
            trajet.is_active = False
            trajet.save()
            messages.success(request, "Trajet recu. Il sera publie apres verification.")
            return redirect("transport:accueil")
        messages.error(request, "Verifiez les informations du trajet.")
    else:
        form = TrajetForm()
    return render(request, "transport_core/publier.html", {"form": form})


def demande(request):
    if request.method == "POST":
        form = DemandeTrajetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Demande publiee. Un conducteur pourra vous contacter.")
            return redirect("transport:accueil")
        messages.error(request, "Verifiez les informations de la demande.")
    else:
        form = DemandeTrajetForm()
    demandes = DemandeTrajet.objects.filter(is_active=True, date_souhaitee__gte=timezone.localdate()).select_related("depart", "arrivee")[:10]
    return render(request, "transport_core/demande.html", {"form": form, "demandes": demandes})
