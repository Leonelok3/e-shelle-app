"""
e_shelle_ai/services/tools/content_writer.py
Génération de contenu textuel spécialisé (descriptions, posts, emails, menus…)
Adapté au marché africain et aux modules E-Shelle.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


CONTENT_TEMPLATES = {
    "description_produit": """Tu es un expert en copywriting e-commerce pour le marché africain francophone.
Rédige une description de produit accrocheuse pour E-Shelle Boutique.
Produit : {subject}
Contexte : {context}
Format : titre percutant + 2-3 paragraphes + liste d'avantages + appel à l'action
Langue : Français, ton enthousiaste mais professionnel, prix en FCFA si pertinent.""",

    "description_restaurant": """Tu es un expert en marketing de restauration pour l'Afrique.
Rédige une description attrayante pour un restaurant sur E-Shelle Resto.
Restaurant / Plat : {subject}
Contexte : {context}
Format : accroche poétique + description des saveurs + ambiance + appel à la réservation
Langue : Français, ton chaleureux et appétissant.""",

    "post_facebook": """Tu es un expert social media pour entrepreneurs africains.
Rédige un post Facebook engageant pour une publication commerciale.
Sujet : {subject}
Contexte : {context}
Format : accroche forte (max 2 lignes) + corps + emojis pertinents + hashtags + CTA
Longueur : 150-250 mots. Adapté au public camerounais/africain.""",

    "post_instagram": """Tu es un expert Instagram pour le marché africain.
Rédige une légende Instagram impactante.
Sujet : {subject}
Contexte : {context}
Format : première ligne accrocheuse + histoire courte + emojis + 10-15 hashtags pertinents (#Cameroun #DoublaBusiness etc.)
Style : authentique, moderne, engageant.""",

    "message_whatsapp": """Tu es un expert en marketing WhatsApp Business pour entrepreneurs africains.
Rédige un message WhatsApp commercial efficace.
Sujet : {subject}
Contexte : {context}
Format : salutation personnalisée + offre claire + avantage clé + CTA simple + cordialités
Longueur : court (max 100 mots), direct, chaleureux. Sans formalisme excessif.""",

    "email_marketing": """Tu es un expert en email marketing pour le marché francophone africain.
Rédige un email marketing professionnel.
Sujet : {subject}
Contexte : {context}
Format : objet accrocheur + salutation + corps structuré + offre claire + CTA bouton + signature
Longueur : 200-300 mots. Professionnel mais chaleureux.""",

    "description_formation": """Tu es un expert en marketing e-learning pour l'Afrique.
Rédige une description de formation attrayante pour EduCam Pro / E-Shelle Formations.
Formation : {subject}
Contexte : {context}
Format : promesse de transformation + ce que vous apprendrez (liste) + pour qui + prix FCFA + inscription
Ton : motivant, axé résultats, crédible.""",

    "faq": """Tu es un expert en service client pour une plateforme africaine.
Génère une FAQ de 5 questions-réponses pour :
Sujet : {subject}
Contexte : {context}
Format : Q: ... R: ... (x5)
Ton : clair, rassurant, professionnel.""",

    "plan_marketing": """Tu es un consultant en marketing digital spécialisé Afrique.
Crée un plan marketing digital pour :
Business : {subject}
Contexte : {context}
Format structuré :
1. Analyse rapide (cible, marché)
2. Canaux recommandés (Facebook/Instagram/WhatsApp/TikTok)
3. Contenu à créer (avec exemples concrets)
4. Budget indicatif en FCFA
5. KPIs à suivre
6. Quick wins (actions immédiates)
Adapté au contexte camerounais, budget réaliste.""",
}


def generate_content(content_type: str, subject: str, context: str = "", user=None) -> str:
    """
    Génère du contenu textuel via GPT-4o.

    Args:
        content_type: Clé de CONTENT_TEMPLATES
        subject:      Sujet/produit/thème
        context:      Contexte additionnel
        user:         Utilisateur (pour personnalisation)

    Returns:
        Contenu généré en texte
    """
    from openai import OpenAI

    template = CONTENT_TEMPLATES.get(content_type)
    if not template:
        # Type inconnu → prompt générique
        template = "Rédige un contenu professionnel en français pour : {subject}. Contexte : {context}"

    prompt = template.format(subject=subject, context=context or "E-Shelle, plateforme africaine")

    # Enrichissement avec contexte utilisateur
    if user:
        try:
            ville = user.profile.ville if hasattr(user, "profile") else "Cameroun"
            prompt += f"\n\nContexte utilisateur : ville={ville}"
        except Exception:
            pass

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=getattr(settings, "OPENAI_CHAT_MODEL", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un expert en marketing et copywriting pour l'Afrique francophone. "
                        "Tu rédiges uniquement en français. "
                        "Tes réponses sont immédiatement utilisables, sans introduction ni conclusion méta."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.75,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Content generation error ({content_type}): {e}")
        return f"Désolé, impossible de générer le contenu pour l'instant. Erreur : {str(e)[:100]}"


def list_content_types() -> list:
    """Retourne la liste des types de contenu disponibles."""
    labels = {
        "description_produit":     "📦 Description produit",
        "description_restaurant":  "🍽️ Description restaurant/plat",
        "post_facebook":           "📘 Post Facebook",
        "post_instagram":          "📸 Légende Instagram",
        "message_whatsapp":        "💬 Message WhatsApp Business",
        "email_marketing":         "📧 Email marketing",
        "description_formation":   "📚 Description de formation",
        "faq":                     "❓ FAQ produit/service",
        "plan_marketing":          "📊 Plan marketing digital",
    }
    return [{"key": k, "label": v} for k, v in labels.items()]
