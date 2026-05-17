from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tchaslucpay.transactions"
    label = "tchaslucpay_transactions"
    verbose_name = "Tchaslucpay - transactions"

