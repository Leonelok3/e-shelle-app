from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentification
    path("accounts/", include("accounts.urls")),

    # Anciens dashboards (compatibilité)
    path("dash/", include("progress.urls")),

    # Modules E-Shelle SaaS
    path("formations/",  include("formations.urls",  namespace="formations")),
    path("boutique/",    include("boutique.urls",    namespace="boutique")),
    path("services/",    include("services.urls",    namespace="services")),
    path("dashboard/",   include("dashboard.urls",   namespace="dashboard")),
    path("payments/",    include("payments.urls",    namespace="payments")),
    path("ia/",          include("ai_engine.urls",   namespace="ai_engine")),

    # API REST
    path("api/v1/",      include("api.urls",         namespace="api")),

    # Abonnements
    path("billing/",     include("billing.urls",         namespace="billing")),

    # MathCM — Mathématiques secondaire MINESEC
    path("maths/", include("math_cm.urls", namespace="math_cm")),

    # Hub des langues
    path("langues/", TemplateView.as_view(template_name="langues/hub.html"), name="langues_hub"),

    # Cours de langues
    path("anglais/",     include("EnglishPrepApp.urls",    namespace="englishprep")),
    path("allemand/",    include("GermanPrepApp.urls",     namespace="germanprep")),
    path("italien/",     include("italian_courses.urls",   namespace="italian_courses")),
    path("prep/",        include("preparation_tests.urls", namespace="preparation_tests")),

    # Immobilier Cameroun
    path("immobilier/", include("immobilier_cameroun.urls", namespace="immobilier")),

    # Auto Cameroun
    path("auto/", include("auto_cameroun.urls", namespace="auto")),

    # Page d'accueil
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
