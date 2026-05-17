from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ClientProfileViewSet,
    CollecteurProfileViewSet,
    MeAPIView,
    RegisterAPIView,
    TchaslucpayLoginView,
    TchaslucpayLogoutView,
    UserViewSet,
)

app_name = "tchaslucpay_accounts"

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("collecteurs", CollecteurProfileViewSet, basename="collecteurs")
router.register("clients", ClientProfileViewSet, basename="clients")

urlpatterns = [
    path("login/", TchaslucpayLoginView.as_view(), name="login"),
    path("logout/", TchaslucpayLogoutView.as_view(), name="logout"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("me/", MeAPIView.as_view(), name="me"),
    path("", include(router.urls)),
]

