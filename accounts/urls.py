from django.urls import path
from django.contrib.auth import views as auth_views
from .views import AppLoginView, AppLogoutView, role_redirect, register, profil

app_name = "accounts"

urlpatterns = [
    path("login/",           AppLoginView.as_view(),                          name="login"),
    path("logout/",          AppLogoutView.as_view(),                         name="logout"),
    path("go/",              role_redirect,                                   name="go"),
    path("register/",        register,                                        name="register"),
    path("profil/",          profil,                                          name="profil"),
    path("password/change/", auth_views.PasswordChangeView.as_view(
        template_name="accounts/password_change.html",
        success_url="/accounts/password/change/done/",
    ), name="password_change"),
    path("password/change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="accounts/password_change_done.html",
    ), name="password_change_done"),
]
