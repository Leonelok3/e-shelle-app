"""
e_shelle_ai/services/context_builder.py
Construit le contexte personnalisé injecté dans chaque appel GPT-4o.
S'adapte dynamiquement aux modules E-Shelle installés et futurs.
"""
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

# Fuseau horaire Cameroun (WAT = UTC+1, pas de DST)
CAMEROUN_OFFSET = timedelta(hours=1)
CAMEROUN_TZ = timezone(CAMEROUN_OFFSET, name="WAT")

# Registre dynamique des modules E-Shelle
# Chaque module peut déclarer ses données en implémentant get_user_data(user)
MODULE_REGISTRY = {}


def register_module(key: str, label: str, icon: str, get_data_fn=None):
    """
    Enregistre un module E-Shelle dans le registre de l'agent IA.
    Appelé au démarrage de chaque app via AppConfig.ready().
    """
    MODULE_REGISTRY[key] = {
        "label":    label,
        "icon":     icon,
        "get_data": get_data_fn,  # callable(user) → dict ou None
    }


def _discover_modules() -> list:
    """
    Découvre automatiquement les modules E-Shelle installés dans Django.
    Retourne la liste des apps disponibles.
    """
    from django.apps import apps
    known = {
        "resto":      ("E-Shelle Resto",     "🍽️"),
        "boutique":   ("E-Shelle Boutique",   "🛒"),
        "formations": ("Formations",          "📚"),
        "agro":       ("E-Shelle Agro",       "🌿"),
        "gaz":        ("E-Shelle Gaz",        "🔥"),
        "pharma":     ("E-Shelle Pharma",     "💊"),
        "pressing":   ("E-Shelle Pressing",   "👔"),
        "rencontres": ("E-Shelle Love",       "❤️"),
        "njangi":     ("Njangi Digital",      "🤝"),
        "immobilier_cameroun": ("E-Shelle Immo", "🏠"),
        "auto_cameroun": ("E-Shelle Auto",   "🚗"),
        "annonces_cam": ("Annonces Cam",     "📢"),
        "adgen":      ("AdGen IA",           "✨"),
        "edu_platform": ("EduCam Pro",       "🎓"),
        "math_cm":    ("MathCM",             "📐"),
    }
    installed = []
    for app_name, (label, icon) in known.items():
        try:
            apps.get_app_config(app_name)
            installed.append({"key": app_name, "label": label, "icon": icon})
        except LookupError:
            pass
    return installed


def _get_user_plan_label(user) -> str:
    try:
        return user.profile.get_plan_display() if hasattr(user.profile, 'get_plan_display') else user.profile.plan
    except Exception:
        return "Gratuit"


def _get_user_ville(user) -> str:
    try:
        return user.profile.ville or "Cameroun"
    except Exception:
        return "Cameroun"


def _get_ai_quota_summary(user) -> str:
    try:
        from e_shelle_ai.services.quota_service import QuotaService
        rem = QuotaService().get_remaining(user)
        return f"Plan IA: {rem['plan']} — {rem['messages']} messages restants ce mois"
    except Exception:
        return ""


class UserContextBuilder:
    """
    Construit le contexte riche injecté dans chaque appel GPT-4o.
    Conçu pour s'adapter aux nouveaux modules E-Shelle ajoutés dans le futur.
    """

    def build(self, user) -> dict:
        """
        Retourne un dict de contexte complet pour l'utilisateur.
        """
        now_cm = datetime.now(CAMEROUN_TZ)
        modules_installed = _discover_modules()

        ctx = {
            "prenom":       user.first_name or user.username,
            "nom_complet":  user.get_full_name() or user.username,
            "username":     user.username,
            "email":        user.email,
            "ville":        _get_user_ville(user),
            "plan":         _get_user_plan_label(user),
            "date_inscription": user.date_joined.strftime("%d/%m/%Y") if user.date_joined else "—",
            "datetime_cm":  now_cm.strftime("%A %d %B %Y à %H:%M (heure Cameroun)"),
            "modules_installes": modules_installed,
            "quota_summary": _get_ai_quota_summary(user),
            "memoire": "",
            "business_context": {},
            "preferences": {},
        }

        # Mémoire long terme
        try:
            from e_shelle_ai.models import AIUserMemory
            mem = AIUserMemory.objects.filter(user=user).first()
            if mem:
                ctx["memoire"]          = mem.get_summary_for_prompt()
                ctx["business_context"] = mem.business_context or {}
                ctx["preferences"]      = mem.preferences or {}
        except Exception:
            pass

        # Données modules dynamiques (via registre)
        ctx["modules_data"] = {}
        for key, info in MODULE_REGISTRY.items():
            if info.get("get_data"):
                try:
                    data = info["get_data"](user)
                    if data:
                        ctx["modules_data"][key] = data
                except Exception as e:
                    logger.debug(f"Module {key} data error: {e}")

        return ctx

    def build_system_prompt(self, user_context: dict) -> str:
        """
        Génère le system prompt complet et dynamique pour GPT-4o.
        Le prompt inclut :
        - Rôle et personnalité de l'agent
        - Contexte utilisateur
        - Modules E-Shelle disponibles
        - Expertise marketing Afrique
        - Instructions de réponse
        """
        modules = user_context.get("modules_installes", [])
        modules_str = ", ".join(
            f"{m['icon']} {m['label']}" for m in modules
        ) if modules else "Modules de base E-Shelle"

        memoire_str = user_context.get("memoire", "")
        business_ctx = user_context.get("business_context", {})
        preferences  = user_context.get("preferences", {})

        business_str = ""
        if business_ctx:
            business_str = "Contexte business : " + ", ".join(f"{k}={v}" for k, v in business_ctx.items())
        if preferences:
            business_str += " | Préférences : " + ", ".join(f"{k}={v}" for k, v in preferences.items())

        prompt = f"""Tu es E-Shelle AI, l'agent intelligent central de la plateforme E-Shelle (e-shelle.com).
E-Shelle est une super-plateforme SaaS africaine qui regroupe plusieurs services numériques pour les entrepreneurs, commerçants et particuliers du Cameroun et d'Afrique.

══════════════════════════════════════════
IDENTITÉ ET MISSION
══════════════════════════════════════════
Tu es un expert polyvalent qui maîtrise :
1. La plateforme E-Shelle et tous ses modules (présents et futurs)
2. Le marketing digital adapté au marché africain
3. Les stratégies de vente à l'ère de l'IA et du digital
4. L'entrepreneuriat au Cameroun (contexte économique, réglementaire, culturel)
5. Le e-commerce, la création de contenu, la croissance d'audience
6. La gestion d'entreprise et l'automatisation intelligente

Tu aides les utilisateurs à :
- Créer, vendre et gérer leurs services sur E-Shelle
- Développer leur business grâce au marketing digital
- Comprendre et exploiter l'IA pour leur croissance
- Trouver les meilleurs services E-Shelle selon leurs besoins
- Optimiser leur présence en ligne et leurs ventes
- Automatiser leurs processus pour gagner du temps

══════════════════════════════════════════
PROFIL UTILISATEUR ACTUEL
══════════════════════════════════════════
Prénom : {user_context.get('prenom', 'Utilisateur')}
Ville : {user_context.get('ville', 'Cameroun')}
Plan : {user_context.get('plan', 'Gratuit')}
Date/heure : {user_context.get('datetime_cm', '')}
{user_context.get('quota_summary', '')}
{memoire_str}
{business_str}

══════════════════════════════════════════
MODULES E-SHELLE DISPONIBLES
══════════════════════════════════════════
{modules_str}

La plateforme E-Shelle est modulaire et s'enrichit régulièrement de nouveaux services.
Tu dois toujours te tenir au courant des modules actifs et orienter l'utilisateur vers les bons outils.

══════════════════════════════════════════
EXPERTISE MARKETING & CROISSANCE (AFRIQUE)
══════════════════════════════════════════
Tu es un expert en marketing digital pour l'Afrique subsaharienne. Tu maîtrises :

📱 MARKETING MOBILE FIRST
- WhatsApp Business : catalogue, messages automatiques, groupes, statuts
- Facebook & Instagram : publicités ciblées, reels, stories
- TikTok : tendances africaines, contenu viral, hashtags
- YouTube : SEO vidéo, shorts, monétisation

🎯 STRATÉGIES DE VENTE
- Techniques de copywriting pour le marché africain
- Prix en FCFA : psychologie du prix, offres packagées, promotions
- Témoignages clients et preuve sociale
- Vente par confiance (bouche-à-oreille, communauté)
- Mobile Money : MTN, Orange Money, Airtel — intégration paiement

🤖 IA & AUTOMATISATION
- Chatbots WhatsApp pour répondre aux clients 24h/24
- Génération de contenu IA (descriptions, posts, publicités)
- Analyse de données clients et personnalisation
- Automatisation des commandes et du service client
- Email marketing automatisé

📊 CROISSANCE & ACQUISITION
- SEO local (Google My Business, Maps)
- Marketing d'influence africain (micro-influenceurs)
- Programmes de fidélité et parrainage
- Événements et pop-up stores
- Bouche-à-oreille numérique et communautés WhatsApp

══════════════════════════════════════════
RÈGLES DE RÉPONSE
══════════════════════════════════════════
- Réponds TOUJOURS en français
- Tous les prix en FCFA (Franc CFA)
- Ton : professionnel, chaleureux, motivant — comme un mentor bienveillant
- Sois concret, actionnable, adapté au contexte camerounais/africain
- Si la question concerne un module E-Shelle, oriente vers la bonne section
- Utilise des emojis avec modération pour structurer tes réponses
- Propose toujours une prochaine étape concrète
- Mémorise les informations importantes partagées par l'utilisateur
- Si tu ne sais pas quelque chose, dis-le honnêtement et propose une alternative

══════════════════════════════════════════
FORMAT DES RÉPONSES
══════════════════════════════════════════
- Réponses structurées avec des titres clairs quand c'est long
- Listes à puces pour les étapes et conseils
- **Gras** pour les points importants
- Maximum 600 mots sauf si une réponse complète est nécessaire
- Toujours terminer par une question ou proposition d'action suivante"""

        return prompt
