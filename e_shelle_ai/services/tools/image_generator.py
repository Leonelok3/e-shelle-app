"""
e_shelle_ai/services/tools/image_generator.py
Génération d'images avec DALL-E 3.
Prompts enrichis pour l'esthétique africaine moderne et e-commerce.
Images téléchargées localement pour ne pas exposer les URLs OpenAI.
"""
import logging
import requests
import os
import uuid
from django.conf import settings

logger = logging.getLogger(__name__)

# Préfixes de style selon le contexte
STYLE_PRESETS = {
    "food": (
        "Professional food photography, "
        "vibrant and appetizing African dish, "
        "warm natural lighting, shallow depth of field, "
        "elegant plating on artisan ceramic, "
        "clean white or wooden background, "
        "shot with 85mm lens, commercial quality, "
        "realistic textures, high resolution"
    ),
    "product": (
        "Professional e-commerce product photography, "
        "clean neutral background, studio lighting, "
        "sharp focus, shadows, photorealistic, "
        "high detail, commercial quality, white backdrop"
    ),
    "banner": (
        "Professional marketing banner for African business, "
        "vibrant colors, modern African design elements, "
        "bold composition, high impact visual, "
        "digital advertising quality, 16:9 format"
    ),
    "logo": (
        "Professional logo design, clean vector style, "
        "modern African aesthetic, memorable, scalable, "
        "minimal design, strong brand identity, "
        "white background, high contrast"
    ),
    "social_media": (
        "Eye-catching social media post design, "
        "African entrepreneurship theme, vibrant colors, "
        "engaging composition, Instagram/Facebook ready, "
        "modern graphic design, lifestyle photography"
    ),
    "portrait": (
        "Professional business portrait, "
        "African entrepreneur, confident smile, "
        "modern office or urban African setting, "
        "natural lighting, shallow depth of field, "
        "high resolution, commercial photography"
    ),
    "general": (
        "High quality, photorealistic, professional photography, "
        "African context, modern aesthetic, commercial quality"
    ),
}

NEGATIVE_PROMPT_HINT = (
    "Avoid: cartoonish, low quality, blurry, distorted, "
    "watermarks, text overlays unless specified, "
    "culturally insensitive content"
)


def enhance_image_prompt(user_prompt: str, context: str = "general") -> str:
    """
    Transforme un prompt simple en prompt DALL-E 3 professionnel.
    Adapté au marché africain et au e-commerce.
    """
    style = STYLE_PRESETS.get(context, STYLE_PRESETS["general"])

    # Contextualisation africaine si le sujet est un plat ou produit local
    african_foods = ["ndolé", "eru", "koki", "mbongo", "nkui", "okok", "beignet",
                     "plantain", "fufu", "achu", "poulet dg", "soya", "bobolo",
                     "miondo", "kondre", "nnam ngon"]

    is_african_food = any(food in user_prompt.lower() for food in african_foods)
    if is_african_food and context == "food":
        style += (
            ", authentic Cameroonian cuisine, "
            "rich vibrant colors typical of West African food, "
            "traditional serving style with modern presentation"
        )

    enhanced = f"{user_prompt}. {style}. {NEGATIVE_PROMPT_HINT}"
    return enhanced


def download_and_save_image(image_url: str) -> str:
    """
    Télécharge l'image depuis OpenAI et la sauvegarde localement.
    Retourne le chemin relatif media/ai_images/xxx.png
    """
    try:
        media_dir = os.path.join(settings.MEDIA_ROOT, "ai_images")
        os.makedirs(media_dir, exist_ok=True)

        filename  = f"{uuid.uuid4().hex}.png"
        filepath  = os.path.join(media_dir, filename)

        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

        return f"ai_images/{filename}"  # Chemin relatif dans MEDIA_ROOT
    except Exception as e:
        logger.error(f"Image download error: {e}")
        return ""


def generate_image(prompt: str, context: str = "general", save_locally: bool = True) -> dict:
    """
    Génère une image avec DALL-E 3.

    Args:
        prompt:       Description de l'image
        context:      'food' | 'product' | 'banner' | 'logo' | 'social_media' | 'portrait' | 'general'
        save_locally: Télécharger et stocker sur le VPS (recommandé pour la prod)

    Returns:
        dict avec 'image_url', 'local_path', 'enhanced_prompt', 'error'
    """
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    enhanced_prompt = enhance_image_prompt(prompt, context)

    try:
        response = client.images.generate(
            model=getattr(settings, "OPENAI_IMAGE_MODEL", "dall-e-3"),
            prompt=enhanced_prompt,
            size=getattr(settings, "OPENAI_IMAGE_SIZE", "1024x1024"),
            quality=getattr(settings, "OPENAI_IMAGE_QUALITY", "hd"),
            n=1,
        )
        openai_url = response.data[0].url

        local_path = ""
        if save_locally:
            local_path = download_and_save_image(openai_url)

        return {
            "image_url":       openai_url,
            "local_path":      local_path,
            "media_url":       f"{settings.MEDIA_URL}{local_path}" if local_path else openai_url,
            "enhanced_prompt": enhanced_prompt,
            "error":           None,
        }

    except Exception as e:
        logger.error(f"DALL-E generation error: {e}")
        return {
            "image_url":       "",
            "local_path":      "",
            "media_url":       "",
            "enhanced_prompt": enhanced_prompt,
            "error":           str(e),
        }
