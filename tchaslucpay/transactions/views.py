from django.http import HttpResponse
from rest_framework import decorators, permissions, response, status, views, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from tchaslucpay.accounts.permissions import IsAdminUser, IsCollecteurUser

from .models import AccountBalance, Transaction
from .serializers import AccountBalanceSerializer, CollecteurTransactionSerializer, PostTransactionSerializer, TransactionSerializer
from .services import render_statement_pdf, reverse_transaction


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = Transaction.objects.select_related("account", "collector", "created_by").all()
        user = self.request.user
        if getattr(user, "role", None) == "ADMIN":
            return qs
        if getattr(user, "role", None) == "COLLECTEUR":
            return qs.filter(collector=user)
        qs = qs.filter(account=user)
        return qs

    @decorators.action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def post_entry(self, request):
        serializer = PostTransactionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        entry = serializer.save()
        return response.Response(TransactionSerializer(entry).data, status=201)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reverse(self, request, pk=None):
        result = reverse_transaction(transaction_id=pk, created_by=request.user, reason=request.data.get("reason", "Correction"))
        return response.Response(TransactionSerializer(result.transaction).data, status=201)

    @decorators.action(detail=False, methods=["get"])
    def statement_pdf(self, request):
        pdf = render_statement_pdf(request.user, start=request.query_params.get("start"), end=request.query_params.get("end"))
        res = HttpResponse(pdf, content_type="application/pdf")
        res["Content-Disposition"] = 'attachment; filename="releve-tchaslucpay.pdf"'
        return res


class AccountBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccountBalanceSerializer

    def get_queryset(self):
        qs = AccountBalance.objects.select_related("user").all()
        return qs if getattr(self.request.user, "role", None) == "ADMIN" else qs.filter(user=self.request.user)


class BaseCollecteurTransactionAPIView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsCollecteurUser]
    type_op = None

    def post(self, request):
        serializer = CollecteurTransactionSerializer(data=request.data, context={"request": request}, type_op=self.type_op)
        serializer.is_valid(raise_exception=True)
        transaction_obj = serializer.save()
        return response.Response(TransactionSerializer(transaction_obj).data, status=status.HTTP_201_CREATED)


class DepotAPIView(BaseCollecteurTransactionAPIView):
    type_op = "DEPOT"


class RetraitAPIView(BaseCollecteurTransactionAPIView):
    type_op = "RETRAIT"
