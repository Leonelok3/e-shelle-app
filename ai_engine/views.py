"""
ai_engine/views.py — Vues IA E-Shelle
Génération de contenu, chat IA, streaming SSE.
"""
import json
import os
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import GenerationIA, TemplatePrompt


@login_required
def generateur(request):
    """Interface de génération de contenu IA."""
    templates = TemplatePrompt.objects.filter(actif=True).order_by("type_gen")
    return render(request, "ai_engine/generateur.html", {"templates": templates})


@csrf_exempt
@login_required
def stream_generate(request):
    """
    Endpoint SSE : génère du contenu IA en streaming via l'API Anthropic.
    POST { prompt, type_gen, modele? }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST requis"}, status=405)

    try:
        data      = json.loads(request.body)
        prompt    = data.get("prompt", "").strip()
        type_gen  = data.get("type_gen", "contenu")
        modele    = data.get("modele", "claude-haiku-4-5-20251001")
    except Exception:
        return JsonResponse({"error": "JSON invalide"}, status=400)

    if not prompt:
        return JsonResponse({"error": "Prompt vide"}, status=400)

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key.startswith("sk-ant-VOTRE"):
        return JsonResponse({"error": "Clé API Anthropic non configurée."}, status=503)

    def event_stream():
        import anthropic
        start = timezone.now()
        resultat_parts = []
        statut = "succes"
        tokens_in = tokens_out = 0

        try:
            client = anthropic.Anthropic(api_key=api_key)
            with client.messages.stream(
                model=modele,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
                system=(
                    "Tu es un assistant expert en création de contenu éducatif et marketing "
                    "pour la plateforme E-Shelle, ciblant les entrepreneurs africains. "
                    "Réponds en français, de façon claire et structurée."
                ),
            ) as stream:
                for chunk in stream.text_stream:
                    resultat_parts.append(chunk)
                    payload = json.dumps({"chunk": chunk})
                    yield f"data: {payload}\n\n"

                # Statistiques finales
                final_msg = stream.get_final_message()
                tokens_in  = final_msg.usage.input_tokens
                tokens_out = final_msg.usage.output_tokens

        except Exception as e:
            statut = "erreur"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        # Sauvegarder la génération en base
        duree = int((timezone.now() - start).total_seconds() * 1000)
        GenerationIA.objects.create(
            utilisateur=request.user,
            type_gen=type_gen,
            modele=modele,
            prompt=prompt[:2000],
            resultat="".join(resultat_parts)[:8000],
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            statut=statut,
            duree_ms=duree,
        )
        yield f"data: {json.dumps({'done': True, 'tokens': tokens_out})}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@login_required
def historique_ia(request):
    """Historique des générations IA de l'utilisateur."""
    generations = GenerationIA.objects.filter(
        utilisateur=request.user
    ).order_by("-created_at")[:50]
    return render(request, "ai_engine/historique.html", {"generations": generations})
