from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import (
    Classe, Chapitre, Lecon, Exercice, EpreuveExamen,
    ProfilEleve, ProgressionLecon, ResultatExercice, ResultatEpreuve
)
import json


def accueil(request):
    classes = Classe.objects.filter(is_active=True)
    stats = {
        'nb_chapitres': Chapitre.objects.filter(is_published=True).count(),
        'nb_exercices': Exercice.objects.filter(is_published=True).count(),
        'nb_epreuves': EpreuveExamen.objects.filter(is_published=True).count(),
    }
    epreuves = EpreuveExamen.objects.filter(is_published=True).select_related('classe')[:6]
    return render(request, 'math_cm/accueil.html', {
        'classes': classes, 'stats': stats, 'epreuves': epreuves
    })


def choisir_classe(request):
    classes = Classe.objects.filter(is_active=True)
    return render(request, 'math_cm/choisir_classe.html', {'classes': classes})


def liste_chapitres(request, classe_nom):
    classe = get_object_or_404(Classe, nom=classe_nom, is_active=True)
    chapitres = Chapitre.objects.filter(classe=classe, is_published=True).select_related('classe')
    categorie = request.GET.get('categorie', 'tous')
    if categorie != 'tous':
        chapitres = chapitres.filter(categorie=categorie)

    progression_map = {}
    if request.user.is_authenticated:
        try:
            profil = request.user.profil_eleve
            for ch in chapitres:
                total = ch.lecons.count()
                done = ProgressionLecon.objects.filter(
                    eleve=profil, lecon__chapitre=ch, completed=True
                ).count()
                progression_map[ch.id] = round((done / total * 100) if total > 0 else 0)
        except ProfilEleve.DoesNotExist:
            pass

    return render(request, 'math_cm/liste_chapitres.html', {
        'classe': classe,
        'chapitres': chapitres,
        'progression_map': progression_map,
        'categories': Chapitre.CATEGORIES,
        'categorie_active': categorie,
    })


def detail_chapitre(request, slug):
    chapitre = get_object_or_404(Chapitre, slug=slug, is_published=True)
    lecons = chapitre.lecons.filter(is_published=True).order_by('ordre')
    exercices = chapitre.exercices.filter(is_published=True).order_by('numero')
    progression = {}
    if request.user.is_authenticated:
        try:
            profil = request.user.profil_eleve
            for lecon in lecons:
                prog = ProgressionLecon.objects.filter(eleve=profil, lecon=lecon).first()
                progression[lecon.id] = prog.completed if prog else False
        except ProfilEleve.DoesNotExist:
            pass
    return render(request, 'math_cm/detail_chapitre.html', {
        'chapitre': chapitre, 'lecons': lecons,
        'exercices': exercices, 'progression': progression,
    })


@login_required
def cours_detail(request, chap_slug, lecon_slug):
    chapitre = get_object_or_404(Chapitre, slug=chap_slug)
    lecon = get_object_or_404(Lecon, slug=lecon_slug, chapitre=chapitre)
    lecons_chapitre = chapitre.lecons.filter(is_published=True).order_by('ordre')
    profil, _ = ProfilEleve.objects.get_or_create(user=request.user)
    prog, _ = ProgressionLecon.objects.get_or_create(eleve=profil, lecon=lecon)
    prog.nb_consultations += 1
    prog.save(update_fields=['nb_consultations'])
    return render(request, 'math_cm/cours_detail.html', {
        'chapitre': chapitre, 'lecon': lecon,
        'lecons_chapitre': lecons_chapitre, 'progression': prog,
        'lecon_prev': lecons_chapitre.filter(ordre__lt=lecon.ordre).last(),
        'lecon_next': lecons_chapitre.filter(ordre__gt=lecon.ordre).first(),
    })


@login_required
@require_POST
def marquer_complete(request, chap_slug, lecon_slug):
    lecon = get_object_or_404(Lecon, slug=lecon_slug)
    profil, _ = ProfilEleve.objects.get_or_create(user=request.user)
    prog, _ = ProgressionLecon.objects.get_or_create(eleve=profil, lecon=lecon)
    if not prog.completed:
        prog.completed = True
        prog.date_completion = timezone.now()
        prog.save()
        profil.points_total += 10
        profil.save(update_fields=['points_total'])
    return JsonResponse({'success': True, 'points': profil.points_total})


@login_required
def exercice_detail(request, pk):
    exercice = get_object_or_404(Exercice, pk=pk, is_published=True)
    profil, _ = ProfilEleve.objects.get_or_create(user=request.user)
    dernier = ResultatExercice.objects.filter(eleve=profil, exercice=exercice).first()
    return render(request, 'math_cm/exercice_detail.html', {
        'exercice': exercice, 'dernier_resultat': dernier,
    })


@login_required
@require_POST
def soumettre_exercice(request, pk):
    exercice = get_object_or_404(Exercice, pk=pk)
    profil, _ = ProfilEleve.objects.get_or_create(user=request.user)
    data = json.loads(request.body)
    reponses = data.get('reponses', {})
    score_auto = data.get('score_auto')  # Auto-évaluation pour exercices ouverts

    if score_auto is not None:
        score = float(score_auto)
    else:
        score = _calculer_score_exercice(exercice, reponses)

    tentative = ResultatExercice.objects.filter(eleve=profil, exercice=exercice).count() + 1
    resultat = ResultatExercice.objects.create(
        eleve=profil, exercice=exercice,
        tentative=tentative, score=score,
        points_obtenus=round(score * exercice.bareme, 1),
        reponses_eleve=reponses,
    )
    points = round(score * 10)
    if points > 0:
        profil.points_total += points
        profil.save(update_fields=['points_total'])
    return JsonResponse({
        'success': True, 'score': round(score * 100),
        'points_obtenus': resultat.points_obtenus,
        'resultat_id': resultat.id,
    })


@login_required
def voir_correction(request, pk):
    exercice = get_object_or_404(Exercice, pk=pk)
    profil, _ = ProfilEleve.objects.get_or_create(user=request.user)
    ResultatExercice.objects.filter(eleve=profil, exercice=exercice).update(correction_consultee=True)
    return JsonResponse({'correction': exercice.correction, 'enonce': exercice.enonce})


def quiz_chapitre(request, slug):
    chapitre = get_object_or_404(Chapitre, slug=slug, is_published=True)
    exercices = list(chapitre.exercices.filter(
        is_published=True, type_exercice='qcm'
    ).values('id', 'titre', 'enonce', 'options_qcm', 'correction')[:10])
    return render(request, 'math_cm/quiz.html', {
        'chapitre': chapitre, 'exercices_json': json.dumps(exercices),
    })


def liste_epreuves(request):
    epreuves = EpreuveExamen.objects.filter(is_published=True).select_related('classe')
    classe_filtre = request.GET.get('classe')
    type_filtre = request.GET.get('type')
    if classe_filtre:
        epreuves = epreuves.filter(classe__nom=classe_filtre)
    if type_filtre:
        epreuves = epreuves.filter(type_examen=type_filtre)
    classes = Classe.objects.filter(is_active=True)
    return render(request, 'math_cm/liste_epreuves.html', {
        'epreuves': epreuves, 'classes': classes,
        'classe_filtre': classe_filtre, 'type_filtre': type_filtre,
    })


def examen_detail(request, slug):
    epreuve = get_object_or_404(EpreuveExamen, slug=slug, is_published=True)
    return render(request, 'math_cm/examen_detail.html', {'epreuve': epreuve})


@login_required
def passer_examen(request, slug):
    epreuve = get_object_or_404(EpreuveExamen, slug=slug, is_published=True)
    if request.method == 'POST':
        data = json.loads(request.body)
        reponses = data.get('reponses', {})
        temps = data.get('temps', 0)
        note = _calculer_note_epreuve(epreuve, reponses)
        profil, _ = ProfilEleve.objects.get_or_create(user=request.user)
        resultat = ResultatEpreuve.objects.create(
            eleve=profil, epreuve=epreuve,
            note=note, temps_passe=temps, reponses=reponses,
        )
        return JsonResponse({'success': True, 'resultat_id': resultat.id})
    return render(request, 'math_cm/examen_blanc.html', {
        'epreuve': epreuve,
        'epreuve_json': json.dumps({'id': epreuve.id, 'titre': epreuve.titre, 'duree': epreuve.duree, 'contenu': epreuve.contenu}),
    })


@login_required
def resultat_epreuve(request, slug, resultat_id):
    epreuve = get_object_or_404(EpreuveExamen, slug=slug)
    profil, _ = ProfilEleve.objects.get_or_create(user=request.user)
    resultat = get_object_or_404(ResultatEpreuve, id=resultat_id, eleve=profil)
    mention = _get_mention(resultat.note)
    return render(request, 'math_cm/resultats_examen.html', {
        'epreuve': epreuve, 'resultat': resultat, 'mention': mention,
    })


@login_required
def progression_eleve(request):
    profil, _ = ProfilEleve.objects.get_or_create(user=request.user)
    progressions = ProgressionLecon.objects.filter(eleve=profil).select_related('lecon__chapitre')
    chapitres_en_cours = {}
    for prog in progressions:
        ch = prog.lecon.chapitre
        if ch.id not in chapitres_en_cours:
            total = ch.lecons.count()
            done = progressions.filter(lecon__chapitre=ch, completed=True).count()
            chapitres_en_cours[ch.id] = {
                'chapitre': ch,
                'pct': round(done / total * 100) if total else 0,
                'done': done, 'total': total,
            }
    resultats = ResultatEpreuve.objects.filter(eleve=profil).select_related('epreuve')[:5]
    return render(request, 'math_cm/progression.html', {
        'profil': profil,
        'chapitres': chapitres_en_cours.values(),
        'resultats': resultats,
    })


@login_required
def api_progression(request):
    profil, _ = ProfilEleve.objects.get_or_create(user=request.user)
    data = {
        'points': profil.points_total,
        'badge': profil.niveau_badge,
        'streak': profil.streak_jours,
    }
    return JsonResponse(data)


def api_stats_chapitre(request, slug):
    chapitre = get_object_or_404(Chapitre, slug=slug)
    return JsonResponse({
        'nb_lecons': chapitre.nb_lecons,
        'nb_exercices': chapitre.nb_exercices,
    })


# ── Helpers ──────────────────────────────────────────────────────────────────

def _calculer_score_exercice(exercice, reponses):
    if exercice.type_exercice == 'qcm':
        bonnes = {opt['label'] for opt in exercice.options_qcm if opt.get('correct')}
        choisies = set(reponses.get('options', []))
        return 1.0 if bonnes == choisies else 0.0
    return 0.5  # Score partiel par défaut pour types non-automatiques


def _calculer_note_epreuve(epreuve, reponses):
    return round(min(20.0, len(reponses) * 0.5), 1)


def _get_mention(note):
    if note >= 16: return ('Très Bien', '#4CAF50')
    if note >= 14: return ('Bien', '#8BC34A')
    if note >= 12: return ('Assez Bien', '#FFC107')
    if note >= 10: return ('Passable', '#FF9800')
    return ('Insuffisant', '#F44336')
