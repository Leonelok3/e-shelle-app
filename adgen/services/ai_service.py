"""
AdGen — Service d'appel à l'API Anthropic
"""
import json
import logging

from django.conf import settings

from .prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class AdGenAIService:

    MODEL = "claude-opus-4-5"
    MAX_TOKENS = 2000

    def __init__(self):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        except ImportError:
            raise RuntimeError("Package 'anthropic' non installé. Lancez: pip install anthropic")

    def generate(self, product_data: dict, modules: list) -> dict:
        """
        Appelle Claude, retourne un dict avec le contenu généré.
        Lève une exception en cas d'échec.
        """
        prompt = PromptBuilder.build(product_data, modules)
        logger.info(f"[AdGen] Génération pour produit='{product_data.get('nom_produit')}' modules={modules}")

        message = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = message.content[0].text.strip()
        tokens_used = message.usage.input_tokens + message.usage.output_tokens

        logger.info(f"[AdGen] Tokens utilisés: {tokens_used}")

        # Nettoyer si l'IA a quand même mis des backticks
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.error(f"[AdGen] JSON invalide reçu de l'API: {e}\nRaw: {raw_text[:500]}")
            raise ValueError(f"Réponse IA invalide (JSON malformé): {e}")

        result["_tokens_used"] = tokens_used
        result["_raw"] = raw_text
        return result
