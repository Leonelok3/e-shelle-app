from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Sécurité
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [h.strip() for h in os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1,e-shelle.com,www.e-shelle.com"
).split(",") if h.strip()]

CSRF_TRUSTED_ORIGINS = [
    "https://e-shelle.com",
    "https://www.e-shelle.com",
]

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",

    "accounts.apps.AccountsConfig",
    "curriculum.apps.CurriculumConfig",
    "content.apps.ContentConfig",
    "progress.apps.ProgressConfig",
    "api.apps.ApiConfig",

    # Modules E-Shelle SaaS
    "formations.apps.FormationsConfig",
    "boutique.apps.BoutiqueConfig",
    "services.apps.ServicesConfig",
    "dashboard.apps.DashboardConfig",
    "ai_engine.apps.AiEngineConfig",
    "payments.apps.PaymentsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "edu_cm.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.media",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "edu_cm.wsgi.application"

# Base de données — SQLite en dev, PostgreSQL en prod (via DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL:
    import urllib.parse as _up
    _u = _up.urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE":   "django.db.backends.postgresql",
            "NAME":     _u.path.lstrip("/"),
            "USER":     _u.username,
            "PASSWORD": _u.password,
            "HOST":     _u.hostname,
            "PORT":     str(_u.port or 5432),
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Mot de passe
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Langue / Heure
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True

# Static / Media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ✅ Custom User (IMPORTANT)
AUTH_USER_MODEL = "accounts.CustomUser"

# Auth redirects
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "accounts:login"

# Auth redirects étendus
LOGIN_REDIRECT_URL = "/dashboard/"

# Anthropic / Claude AI
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Email (dev : console, prod : SMTP)
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST     = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT     = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS  = True
EMAIL_HOST_USER     = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL  = os.getenv("DEFAULT_FROM_EMAIL", "noreply@e-shelle.com")

# Sécurité HTTPS (activée quand DEBUG=False)
if not DEBUG:
    SESSION_COOKIE_SECURE  = os.getenv("SESSION_COOKIE_SECURE",  "True").lower() == "true"
    CSRF_COOKIE_SECURE     = os.getenv("CSRF_COOKIE_SECURE",     "True").lower() == "true"
    SECURE_HSTS_SECONDS    = int(os.getenv("SECURE_HSTS_SECONDS", "63072000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD    = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Taille max upload (fichiers produits digitaux)
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800   # 50 Mo
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800   # 50 Mo

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
