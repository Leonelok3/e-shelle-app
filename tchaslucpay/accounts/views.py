from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from rest_framework import permissions, viewsets
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView

from .models import ClientProfile, CollecteurProfile, UserRole
from .permissions import IsAdminUser
from .serializers import ClientProfileSerializer, CollecteurProfileSerializer, RegisterSerializer, UserSerializer


class TchaslucpayLoginView(LoginView):
    template_name = "tchaslucpay/accounts/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or getattr(user, "role", None) == UserRole.ADMIN:
            return reverse("tchaslucpay_dashboard:admin")
        if getattr(user, "role", None) == UserRole.COLLECTEUR:
            return reverse("tchaslucpay_dashboard:collecteur")
        if getattr(user, "role", None) == UserRole.CLIENT:
            return reverse("tchaslucpay_dashboard:client")
        return reverse("tchaslucpay_dashboard:home")


class TchaslucpayLogoutView(LogoutView):
    next_page = reverse_lazy("tchaslucpay_accounts:login")


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class CollecteurProfileViewSet(viewsets.ModelViewSet):
    queryset = CollecteurProfile.objects.select_related("user").all()
    serializer_class = CollecteurProfileSerializer
    permission_classes = [IsAdminUser]


class ClientProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ClientProfileSerializer

    def get_queryset(self):
        qs = ClientProfile.objects.select_related("user", "trusted_collecteur", "trusted_collecteur__user")
        user = self.request.user
        if getattr(user, "role", None) == "ADMIN":
            return qs
        collecteur = getattr(user, "collecteur_profile", None)
        if collecteur is not None:
            return qs.filter(trusted_collecteur=collecteur)
        return qs.filter(user=user)
