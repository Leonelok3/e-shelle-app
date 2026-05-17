from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AccountBalanceViewSet, DepotAPIView, RetraitAPIView, TransactionViewSet

app_name = "tchaslucpay_transactions"

router = DefaultRouter()
router.register("ledger", TransactionViewSet, basename="ledger")
router.register("balances", AccountBalanceViewSet, basename="balances")

urlpatterns = [
    path("depot/", DepotAPIView.as_view(), name="depot"),
    path("retrait/", RetraitAPIView.as_view(), name="retrait"),
    path("", include(router.urls)),
]
