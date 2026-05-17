from django.conf import settings


def eshelle_public_urls(request):
    """Expose les URLs publiques des modules externes dans les templates."""
    return {
        "TCHASLUCPAY_PUBLIC_URL": getattr(settings, "TCHASLUCPAY_PUBLIC_URL", "http://127.0.0.1:8001/"),
    }
