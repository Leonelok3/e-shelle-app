from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("tchaslucpay.dashboard.urls", namespace="tchaslucpay_dashboard")),
    path("accounts/", include("tchaslucpay.accounts.urls", namespace="tchaslucpay_accounts")),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/accounts/", include("tchaslucpay.accounts.urls", namespace="tchaslucpay_accounts_api")),
    path("api/transactions/", include("tchaslucpay.transactions.urls", namespace="tchaslucpay_transactions")),
]

