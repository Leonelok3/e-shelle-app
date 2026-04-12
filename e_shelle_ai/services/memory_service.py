"""
e_shelle_ai/services/memory_service.py
Gestion de la mémoire court terme (session) et long terme (base de données).
Résumé automatique des conversations longues via GPT-4o.
"""
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)

# Seuil : résumer la mémoire après N messages utilisateur
SUMMARY_THRESHOLD = getattr(settings, "AI_MEMORY_SUMMARY_THRESHOLD", 40)


class MemoryService:
    """Gère la persistance et la consolidation de la mémoire utilisateur."""

    def get_or_create_memory(self, user):
        """Retourne ou crée l'objet AIUserMemory de l'utilisateur."""
        from e_shelle_ai.models import AIUserMemory
        mem, _ = AIUserMemory.objects.get_or_create(user=user)
        return mem

    def should_summarize(self, user) -> bool:
        """Vérifie si la mémoire doit être résumée (trop de messages)."""
        from e_shelle_ai.models import AIMessage
        total = AIMessage.objects.filter(
            conversation__user=user, role="user"
        ).count()
        return total > 0 and total % SUMMARY_THRESHOLD == 0

    def update_memory_from_message(self, user, user_message: str, assistant_reply: str):
        """
        Extrait et met à jour les informations clés du dialogue.
        Détection légère sans appel API — basée sur des patterns.
        """
        try:
            mem = self.get_or_create_memory(user)
            prefs = mem.preferences or {}
            biz   = mem.business_context or {}

            msg_lower = user_message.lower()

            # Détection ville
            villes = ["yaoundé", "douala", "bafoussam", "buea", "limbe",
                      "bamenda", "garoua", "maroua", "bertoua", "ngaoundéré"]
            for v in villes:
                if v in msg_lower:
                    prefs["ville"] = v.capitalize()
                    break

            # Détection secteur d'activité
            secteurs = {
                "restaurant": "restauration",
                "resto": "restauration",
                "manger": "restauration",
                "plat": "restauration",
                "cuisine": "restauration",
                "boutique": "commerce",
                "vente": "commerce",
                "produit": "commerce",
                "vêtement": "mode",
                "pressing": "blanchisserie",
                "pharma": "santé",
                "médicament": "santé",
                "formation": "éducation",
                "cours": "éducation",
                "enseignement": "éducation",
                "immobilier": "immobilier",
                "appartement": "immobilier",
                "terrain": "immobilier",
                "agro": "agriculture",
                "farm": "agriculture",
                "gaz": "énergie",
            }
            for keyword, secteur in secteurs.items():
                if keyword in msg_lower:
                    biz["secteur"] = secteur
                    break

            # Détection objectifs marketing
            if any(w in msg_lower for w in ["vendre", "vente", "client", "chiffre"]):
                biz["objectif"] = "croissance commerciale"
            if any(w in msg_lower for w in ["instagram", "facebook", "tiktok", "réseaux"]):
                biz["reseaux_sociaux"] = "actif"
            if any(w in msg_lower for w in ["whatsapp", "wha"]):
                biz["whatsapp_business"] = "utilise"

            mem.preferences     = prefs
            mem.business_context = biz
            mem.save(update_fields=["preferences", "business_context", "last_updated"])

        except Exception as e:
            logger.error(f"Memory update error pour {user}: {e}")

    def summarize_if_needed(self, user):
        """
        Si le seuil est atteint, résume l'historique via GPT-4o
        et stocke le résumé dans AIUserMemory.summary.
        """
        if not self.should_summarize(user):
            return

        try:
            from e_shelle_ai.models import AIConversation
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            # Récupère les derniers messages significatifs
            convs = AIConversation.objects.filter(user=user, is_active=True)
            all_messages = []
            for conv in convs[:5]:
                for msg in conv.messages.filter(role__in=["user", "assistant"]).order_by("created_at")[:20]:
                    all_messages.append(f"[{msg.role}] {msg.content[:200]}")

            if not all_messages:
                return

            history_str = "\n".join(all_messages[-30:])
            summary_prompt = f"""Résume en 3-5 phrases concises ce que tu sais sur cet utilisateur E-Shelle
à partir de ses conversations. Inclus : son secteur d'activité, ses besoins principaux,
ses projets mentionnés, ses villes d'intérêt, ses objectifs de vente/marketing.
Réponse en français, format compact.

Historique :
{history_str}"""

            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=300,
                temperature=0.3,
            )
            summary = resp.choices[0].message.content.strip()

            mem = self.get_or_create_memory(user)
            mem.summary = summary
            mem.save(update_fields=["summary", "last_updated"])
            logger.info(f"Mémoire résumée pour {user.username}")

        except Exception as e:
            logger.error(f"Memory summarization error: {e}")

    def get_memory_for_prompt(self, user) -> str:
        """Retourne la mémoire formatée pour injection dans le system prompt."""
        try:
            mem = self.get_or_create_memory(user)
            return mem.get_summary_for_prompt()
        except Exception:
            return ""

    def clear_memory(self, user):
        """Efface la mémoire d'un utilisateur (à sa demande)."""
        try:
            from e_shelle_ai.models import AIUserMemory
            AIUserMemory.objects.filter(user=user).update(
                preferences={},
                summary="",
                business_context={},
            )
        except Exception as e:
            logger.error(f"Clear memory error: {e}")
