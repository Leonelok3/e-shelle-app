from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    AppLoginView, AppLogoutView,
    role_redirect, register, profil, verify_email, resend_code,
    mon_compte, upgrade, cancel_subscription, activer_code,
)

app_name = "accounts"

urlpatterns = [
    # ── Authentification ─────────────────────────────────────────
    path("login/",           AppLoginView.as_view(),  name="login"),
    path("logout/",          AppLogoutView.as_view(), name="logout"),
    path("go/",              role_redirect,            name="go"),
    path("register/",        register,                 name="register"),
    path("verify/",          verify_email,             name="verify_email"),
    path("verify/resend/",   resend_code,              name="resend_code"),

    # ── Profil (ancien) ──────────────────────────────────────────
    path("profil/",          profil,                   name="profil"),

    # ── Mot de passe ─────────────────────────────────────────────
    path("password/change/", auth_views.PasswordChangeView.as_view(
        template_name="accounts/password_change.html",
        success_url="/accounts/password/change/done/",
    ), name="password_change"),
    path("password/change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="accounts/password_change_done.html",
    ), name="password_change_done"),

    # ── Mon Compte (nouveau dashboard unifié) ────────────────────
    path("mon-compte/",      mon_compte,               name="mon_compte"),
    path("upgrade/",         upgrade,                  name="upgrade"),
    path("abonnement/<int:pk>/annuler/", cancel_subscription, name="cancel_subscription"),
    path("activer/",       activer_code,             name="activer_code"),
]
