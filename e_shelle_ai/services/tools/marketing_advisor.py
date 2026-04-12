"""
e_shelle_ai/services/tools/marketing_advisor.py
Conseiller marketing IA ultra-poussé pour entrepreneurs africains.
Couvre : digital marketing, IA, automatisation, croissance business.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# ─── Base de connaissances marketing Afrique ────────────────────────────────
# Ces données enrichissent les réponses de l'agent sans appel API additionnel.

MARKETING_KNOWLEDGE = {
    "whatsapp_business": {
        "title": "WhatsApp Business — Stratégie Complète",
        "tips": [
            "Créez un catalogue de produits directement dans WhatsApp Business",
            "Utilisez les messages automatiques (message d'absence, message d'accueil)",
            "Créez des listes de diffusion par segment client (VIP, prospects, anciens clients)",
            "Publiez des statuts quotidiens avec vos offres et nouveautés",
            "Utilisez les étiquettes pour organiser vos conversations (Nouveau client, En cours, Payé)",
            "Intégrez un lien WhatsApp direct sur tous vos supports (wa.me/237...)",
            "Répondez dans les 5 minutes — le taux de conversion chute de 80% après 1h",
        ],
        "tools": ["WhatsApp Business App", "WhatsApp Business API (pour volume élevé)", "Twilio", "360dialog"],
        "cameroun_tip": "Plus de 8 millions de Camerounais utilisent WhatsApp quotidiennement — c'est votre canal principal.",
    },

    "facebook_instagram": {
        "title": "Facebook & Instagram — Publicité Africaine",
        "tips": [
            "Ciblez par ville camerounaise (Yaoundé, Douala, Bafoussam) + âge + intérêts",
            "Budget minimal efficace : 2000-5000 FCFA/jour pour tester",
            "Les vidéos courtes (Reels) ont 3x plus de portée que les photos",
            "Postez entre 12h-14h et 19h-21h (heure de Yaoundé) pour plus d'engagement",
            "Utilisez le pixel Facebook sur votre site pour le retargeting",
            "Créez une audience similaire (Lookalike) depuis vos clients WhatsApp",
            "Témoignages clients en vidéo = contenu le plus performant au Cameroun",
        ],
        "budget_recommande": {
            "debutant": "5000-10000 FCFA/semaine",
            "croissance": "25000-50000 FCFA/semaine",
            "scale": "100000+ FCFA/semaine",
        },
        "cameroun_tip": "Facebook reste N°1 au Cameroun. Instagram monte chez les 18-35 ans urbains.",
    },

    "tiktok": {
        "title": "TikTok — Stratégie Virale Africaine",
        "tips": [
            "Contenu en français + langues locales (ewondo, bassa, duala) pour l'authenticité",
            "Films la préparation/fabrication de vos produits — le 'behind the scenes' cartonne",
            "Utilisez les sons tendance africains (#CamerounTikTok, #DoublaTok)",
            "Collaborez avec des créateurs locaux (100k-500k abonnés = micro-influenceurs)",
            "Minimum 3 vidéos/semaine pour l'algorithme TikTok",
            "Apprenez quelque chose d'utile en 60 secondes = format le plus partagé",
        ],
        "cameroun_tip": "TikTok explose chez les 15-30 ans. Potentiel viral énorme pour les produits locaux.",
    },

    "mobile_money": {
        "title": "Paiement Mobile Money — Intégration Commerce",
        "tips": [
            "MTN MoMo et Orange Money = 90% des paiements mobiles au Cameroun",
            "Affichez clairement vos numéros MoMo sur tous vos supports",
            "Utilisez des codes QR pour faciliter les paiements en boutique",
            "Confirmez immédiatement chaque paiement par WhatsApp",
            "Gardez un registre des transactions (screenshot + carnet)",
            "Proposez 'paiement à la livraison' pour rassurer les nouveaux clients",
        ],
        "solutions_integration": [
            "Campay (API Mobile Money Cameroun)",
            "Monetbil (MTN + Orange Money API)",
            "NotchPay (solution complète Afrique)",
        ],
        "cameroun_tip": "70% des Camerounais bancarisés utilisent le Mobile Money. Acceptez-le obligatoirement.",
    },

    "seo_local": {
        "title": "SEO Local — Être Trouvé sur Google",
        "tips": [
            "Créez et optimisez votre fiche Google My Business (gratuit, puissant)",
            "Demandez des avis Google à chaque client satisfait",
            "Utilisez des mots-clés locaux : 'pressing Yaoundé', 'restaurant Bastos'",
            "Publiez régulièrement sur Google My Business (photos, offres, posts)",
            "Votre site doit être mobile-first et charger en moins de 3 secondes",
            "Inscrivez votre business dans les annuaires locaux (Jumia, Afrimalin)",
        ],
        "cameroun_tip": "Google Maps est massivement utilisé pour trouver des commerces au Cameroun.",
    },

    "ia_automatisation": {
        "title": "IA & Automatisation pour Entrepreneurs Africains",
        "tips": [
            "ChatGPT / E-Shelle AI : génération de descriptions produits, posts, emails en secondes",
            "Chatbot WhatsApp : répondez aux clients 24h/24 automatiquement",
            "E-Shelle AI DALL-E : générez des photos produit professionnelles sans photographe",
            "Automatisation réseaux sociaux : planifiez 1 semaine de posts en 1 heure",
            "Email marketing automatique : séquences de bienvenue, relance panier abandonné",
            "Google Sheets + Make (Integromat) : automatisez vos commandes et inventaire",
            "Canva AI : créez des visuels professionnels pour vos réseaux sociaux en minutes",
        ],
        "gains_temps": {
            "génération_contenu": "3h → 15min avec l'IA",
            "photo_produit": "50000 FCFA → Gratuit avec DALL-E",
            "service_client": "Disponible 24h/24 avec chatbot",
            "gestion_stocks": "Manuel → Automatique avec apps",
        },
        "cameroun_tip": "L'IA vous donne les mêmes outils que les grandes entreprises. Avantage compétitif immédiat.",
    },

    "acquisition_clients": {
        "title": "Acquisition Clients — Stratégies Éprouvées",
        "tips": [
            "Programme de parrainage : -10% pour le client qui recommande + -10% pour le nouveau",
            "Offre de lancement : 3 premiers clients = prix réduit + témoignage vidéo",
            "Présence dans les groupes WhatsApp locaux (quartier, association, église)",
            "Partenariats avec des complémentaires (pressing → pressing livraison, resto → traiteur)",
            "Journée portes ouvertes ou dégustation gratuite = 50+ prospects d'un coup",
            "Cartes de visite digitales (QR code → WhatsApp direct)",
            "Livraison gratuite les 2 premières commandes = conversion x3",
        ],
        "cameroun_tip": "La confiance est reine au Cameroun. Montrez votre visage, racontez votre histoire.",
    },

    "pricing_strategy": {
        "title": "Stratégie de Prix — Maximiser les Revenus",
        "tips": [
            "Prix psychologique : 4999 FCFA vs 5000 FCFA → conversion +15%",
            "Offre packagée : produit A + B + C = économisez 2000 FCFA → panier moyen x2",
            "Tier pricing : Basic / Pro / Premium → les clients choisissent le milieu",
            "Prix d'urgence : -20% avant minuit → déclenche l'achat immédiat",
            "Abonnement mensuel : revenus prévisibles + fidélisation automatique",
            "Upsell : proposez toujours une option supérieure après la commande",
            "Gratuit → Payant : offrez 1 essai gratuit, convertissez ensuite",
        ],
        "cameroun_tip": "Les Camerounais comparent les prix. Justifiez votre valeur ajoutée, ne bradez pas.",
    },

    "fidelisation": {
        "title": "Fidélisation Client — Garder vos Clients",
        "tips": [
            "Carte de fidélité numérique : 10 achats = 1 gratuit (via WhatsApp)",
            "Message personnalisé d'anniversaire avec une offre spéciale",
            "Groupe WhatsApp VIP : offres exclusives, avant-premières",
            "Feedback systématique : demandez un avis après chaque achat",
            "Programme 'Ambassadeur' : vos meilleurs clients deviennent vos commerciaux",
            "Newsletter mensuelle : actualités, conseils, offres (via WhatsApp Broadcast)",
            "Service après-vente irréprochable : problème → solution en moins de 2h",
        ],
        "cameroun_tip": "Acquérir un nouveau client coûte 5x plus cher que garder un client existant.",
    },
}


def get_marketing_advice(topic: str, user=None) -> str:
    """
    Retourne des conseils marketing structurés selon le topic.
    Utilisé pour enrichir le contexte de l'agent IA.
    """
    topic_lower = topic.lower()

    # Correspondance topic → clé base de connaissances
    mapping = {
        ("whatsapp", "wha"): "whatsapp_business",
        ("facebook", "instagram", "meta", "pub"): "facebook_instagram",
        ("tiktok", "vidéo", "viral"): "tiktok",
        ("mobile money", "mtn", "orange money", "paiement"): "mobile_money",
        ("seo", "google", "référencement"): "seo_local",
        ("ia", "intelligence artificielle", "automatisation", "automatique"): "ia_automatisation",
        ("client", "acquisition", "prospect"): "acquisition_clients",
        ("prix", "tarif", "pricing"): "pricing_strategy",
        ("fidél", "loyalty", "retention"): "fidelisation",
    }

    knowledge_key = None
    for keywords, key in mapping.items():
        if any(kw in topic_lower for kw in keywords):
            knowledge_key = key
            break

    if knowledge_key and knowledge_key in MARKETING_KNOWLEDGE:
        data = MARKETING_KNOWLEDGE[knowledge_key]
        tips_str = "\n".join(f"  • {t}" for t in data["tips"])
        result = f"**{data['title']}**\n\n{tips_str}"

        if "cameroun_tip" in data:
            result += f"\n\n💡 **Tip Cameroun :** {data['cameroun_tip']}"

        return result

    return ""


def get_quick_wins(user=None) -> str:
    """
    Retourne 5 actions marketing immédiates personnalisées.
    """
    # Détection du secteur depuis la mémoire utilisateur
    secteur = "business"
    try:
        if user and hasattr(user, "ai_memory"):
            mem = user.ai_memory
            secteur = mem.business_context.get("secteur", "business")
    except Exception:
        pass

    quick_wins = {
        "restauration": [
            "📸 Photographiez votre meilleur plat aujourd'hui et postez sur Facebook + WhatsApp Status",
            "💬 Créez un groupe WhatsApp 'Clients VIP' et ajoutez vos 20 meilleurs clients",
            "⭐ Demandez à 3 clients satisfaits de laisser un avis Google maintenant",
            "🎁 Lancez une offre 'Menu du jour' avec -15% jusqu'à 14h",
            "📍 Mettez à jour votre Google My Business avec vos horaires et photos",
        ],
        "commerce": [
            "📦 Photographiez votre catalogue complet avec l'IA E-Shelle (DALL-E)",
            "💬 Créez votre catalogue WhatsApp Business dans les prochaines 2 heures",
            "🚚 Annoncez la livraison gratuite pour toute commande +5000 FCFA cette semaine",
            "📱 Ajoutez votre lien WhatsApp sur votre profile Instagram et Facebook",
            "⭐ Contactez vos 5 derniers clients pour demander un témoignage vidéo",
        ],
        "éducation": [
            "🎥 Filmez 60 secondes d'un conseil de votre domaine et publiez sur TikTok/Reels",
            "📚 Créez une mini-formation gratuite de 3 vidéos pour capturer des emails",
            "💬 Ouvrez un groupe WhatsApp thématique et invitez 50 personnes",
            "🎁 Offrez un PDF gratuit (guide, checklist) en échange d'un contact WhatsApp",
            "📣 Contactez 2 écoles ou entreprises pour proposer une formation interne",
        ],
        "business": [
            "📱 Passez à WhatsApp Business et activez le message automatique d'accueil",
            "📸 Publiez une photo de votre équipe / espace de travail avec votre histoire",
            "⭐ Créez votre fiche Google My Business si ce n'est pas encore fait",
            "💰 Acceptez le Mobile Money MTN et Orange Money si ce n'est pas le cas",
            "🤝 Contactez 2 business complémentaires pour un partenariat cette semaine",
        ],
    }

    wins = quick_wins.get(secteur, quick_wins["business"])
    result = "**⚡ Quick Wins — Actions à faire maintenant :**\n\n"
    result += "\n".join(f"{i+1}. {w}" for i, w in enumerate(wins))
    result += "\n\n_Ces 5 actions peuvent générer des résultats dans les 48h._"
    return result
