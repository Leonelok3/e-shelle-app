from django.urls import path
from .views import AppLoginView, AppLogoutView, role_redirect

app_name = "accounts"

urlpatterns = [
    path("login/", AppLoginView.as_view(), name="login"),
    path("logout/", AppLogoutView.as_view(), name="logout"),
    path("go/", role_redirect, name="go"),
]
