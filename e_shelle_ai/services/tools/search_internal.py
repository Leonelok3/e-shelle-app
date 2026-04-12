"""
e_shelle_ai/services/tools/search_internal.py
Recherche dans la base de données E-Shelle selon la question de l'utilisateur.
Défensive : fonctionne même si certains modules sont absents.
"""
import logging

logger = logging.getLogger(__name__)


def search_eshelle(query: str, user=None) -> str:
    """
    Recherche multi-modules dans la plateforme E-Shelle.
    Retourne un texte formaté à injecter dans le contexte GPT.
    """
    results = []
    query_lower = query.lower()

    # ── Resto ──────────────────────────────────────────────────────────────
    if any(w in query_lower for w in ["restaurant", "resto", "manger", "food", "plat", "cuisine"]):
        try:
            from resto.models import Restaurant
            restos = Restaurant.objects.filter(is_active=True).select_related("ville")[:5]
            if restos:
                lines = [f"  • {r.nom} — {r.ville.nom if r.ville else ''} ({r.horaires or 'horaires N/A'})" for r in restos]
                results.append("🍽️ Restaurants disponibles sur E-Shelle :\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Resto search error: {e}")

    # ── Pressing ────────────────────────────────────────────────────────────
    if any(w in query_lower for w in ["pressing", "blanchisserie", "vêtement", "linge", "teintur"]):
        try:
            from pressing.models import Pressing
            prs = Pressing.objects.filter(is_active=True, abonnement_actif=True).select_related("ville")[:5]
            if prs:
                lines = [f"  • {p.nom} — {p.ville.nom} ({'Express' if p.express else 'Standard'})" for p in prs]
                results.append("👔 Pressings disponibles :\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Pressing search error: {e}")

    # ── Gaz ────────────────────────────────────────────────────────────────
    if any(w in query_lower for w in ["gaz", "bouteille", "butane", "propane"]):
        try:
            from gaz.models import DepotGaz
            depots = DepotGaz.objects.filter(is_active=True, abonnement_actif=True).select_related("ville")[:5]
            if depots:
                lines = [f"  • {d.nom} — {d.ville.nom}" for d in depots]
                results.append("🔥 Dépôts de gaz disponibles :\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Gaz search error: {e}")

    # ── Pharma ─────────────────────────────────────────────────────────────
    if any(w in query_lower for w in ["pharmacie", "médicament", "ordonnance", "santé", "médecin"]):
        try:
            from pharma.models import Pharmacie, Medicament
            # Recherche médicament
            meds = Medicament.objects.filter(nom__icontains=query)[:3]
            if meds:
                lines = [f"  • {m.nom} ({m.categorie.nom if m.categorie else 'N/A'})" for m in meds]
                results.append("💊 Médicaments trouvés :\n" + "\n".join(lines))
            # Pharmacies
            pharms = Pharmacie.objects.filter(is_active=True).select_related("ville")[:3]
            if pharms:
                lines = [f"  • {p.nom} — {p.ville.nom}" for p in pharms]
                results.append("🏥 Pharmacies disponibles :\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Pharma search error: {e}")

    # ── Immobilier ─────────────────────────────────────────────────────────
    if any(w in query_lower for w in ["appartement", "maison", "terrain", "louer", "acheter", "immo"]):
        try:
            from immobilier_cameroun.models import Annonce
            annonces = Annonce.objects.filter(is_active=True).select_related("ville")[:4]
            if annonces:
                lines = [f"  • {a.titre} — {a.prix:,} FCFA ({a.ville.nom if hasattr(a, 'ville') and a.ville else ''})" for a in annonces]
                results.append("🏠 Annonces immobilières :\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Immo search error: {e}")

    # ── Agro ────────────────────────────────────────────────────────────────
    if any(w in query_lower for w in ["agro", "agricole", "producteur", "récolte", "ferme"]):
        try:
            from agro.models import Producteur
            prods = Producteur.objects.filter(is_active=True).select_related("ville")[:4]
            if prods:
                lines = [f"  • {p.nom} — {p.ville.nom if p.ville else 'N/A'}" for p in prods]
                results.append("🌿 Producteurs Agro :\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Agro search error: {e}")

    # ── Formations ──────────────────────────────────────────────────────────
    if any(w in query_lower for w in ["formation", "cours", "apprendre", "certif", "diplôme"]):
        try:
            from formations.models import Formation
            fms = Formation.objects.filter(is_published=True)[:4]
            if fms:
                lines = [f"  • {f.titre} — {f.prix:,} FCFA" for f in fms]
                results.append("📚 Formations disponibles :\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Formations search error: {e}")

    if not results:
        return ""

    return "\n\n".join(results)
