from django.db import migrations


class Migration(migrations.Migration):
    """
    Supprime duration_months de FundDeposit.
    Les intérêts sont désormais calculés mois par mois via MemberMonthlyStatement.
    """

    dependencies = [
        ('njangi', '0004_add_auditlog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='funddeposit',
            name='duration_months',
        ),
    ]
