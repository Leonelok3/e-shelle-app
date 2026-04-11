"""
Commande de seed Njangi+ — Données de démonstration camerounaises
Usage: python manage.py seed_njangi
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from njangi.models import (
    Group, Membership,
    Session, Contribution,
    FundDeposit, FundTransaction,
    Loan, LoanRepayment,
    Notification,
)

User = get_user_model()

FIRST_NAMES = [
    "Amara", "Boubacar", "Clarisse", "Didier", "Esther",
    "Fernand", "Grâce", "Henri", "Isabelle", "Jean-Paul",
    "Kader", "Laurence", "Marcel", "Nadia", "Olivier",
    "Patience", "Rodrigue", "Sandrine", "Thomas", "Ursule",
]
LAST_NAMES = [
    "Ndongo", "Mbella", "Fotso", "Kamga", "Essomba",
    "Biya", "Atangana", "Nkemdirim", "Tabi", "Manga",
    "Nganou", "Ewolo", "Abah", "Mbida", "Nguele",
]
GROUP_NAMES = [
    "Njangi Bamiléké Yaoundé",
    "Tontine des Amis du Wouri",
    "Solidarité Beti Douala",
    "Njangi Femmes de Bafoussam",
    "Mutuelle des Cadres d'Ebolowa",
]


class Command(BaseCommand):
    help = "Seed Njangi+ avec des données de démonstration camerounaises"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Supprimer les données njangi existantes avant le seed")

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("[clean] Nettoyage des donnees Njangi+ existantes...")
            Contribution.objects.all().delete()
            FundTransaction.objects.all().delete()
            LoanRepayment.objects.all().delete()
            Loan.objects.all().delete()
            FundDeposit.objects.all().delete()
            Notification.objects.all().delete()
            Session.objects.all().delete()
            Membership.objects.all().delete()
            Group.objects.all().delete()
            self.stdout.write(self.style.WARNING("   Tables vidées."))

        # ── 1. Créer des utilisateurs ──────────────────────────────────────────
        self.stdout.write("[*] Creation des utilisateurs...")
        users = []
        for i in range(20):
            fn = FIRST_NAMES[i]
            ln = random.choice(LAST_NAMES)
            username = f"njangi_{fn.lower()}"
            email = f"{fn.lower()}.{ln.lower()}@example.cm"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "first_name": fn, "last_name": ln}
            )
            if created:
                user.set_password("njangi2026")
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"   {len(users)} utilisateurs prêts."))

        # ── 2. Créer un groupe principal ───────────────────────────────────────
        self.stdout.write("[*] Creation des groupes Njangi...")
        group_data = [
            {
                "name": "Njangi Bamiléké Yaoundé",
                "contribution_amount": 25000,
                "frequency": "monthly",
                "fund_loan_rate": 10,
                "fund_deposit_rate": 5,
                "penalty_per_day": 500,
                "max_members": 12,
                "max_loan_multiplier": 3,
                "start_date": date(2025, 1, 1),
            },
            {
                "name": "Tontine des Amis du Wouri",
                "contribution_amount": 50000,
                "frequency": "monthly",
                "fund_loan_rate": 8,
                "fund_deposit_rate": 4,
                "penalty_per_day": 1000,
                "max_members": 10,
                "max_loan_multiplier": 2,
                "start_date": date(2025, 3, 1),
            },
        ]

        for i, gd in enumerate(group_data):
            creator = users[i * 5]
            group, created = Group.objects.get_or_create(
                name=gd["name"],
                defaults={
                    "contribution_amount": gd["contribution_amount"],
                    "frequency": gd["frequency"],
                    "fund_loan_rate": gd["fund_loan_rate"],
                    "fund_deposit_rate": gd["fund_deposit_rate"],
                    "penalty_per_day": gd["penalty_per_day"],
                    "max_members": gd["max_members"],
                    "max_loan_multiplier": gd["max_loan_multiplier"],
                    "start_date": gd["start_date"],
                    "created_by": creator,
                    "status": "active",
                }
            )

            if not created:
                self.stdout.write(f"   Groupe '{group.name}' existe déjà — skipping.")
                continue

            # Membres
            group_users = users[i * 5: i * 5 + min(gd["max_members"], 10)]
            roles = ["president", "treasurer", "secretary"] + ["member"] * 20
            for j, u in enumerate(group_users):
                Membership.objects.create(
                    user=u,
                    group=group,
                    role=roles[j],
                    hand_order=j + 1,
                    is_active=True,
                )

            self.stdout.write(self.style.SUCCESS(f"   Groupe '{group.name}' créé avec {len(group_users)} membres."))

            # ── 3. Séances + cotisations ───────────────────────────────────────
            members = list(group.memberships.filter(is_active=True).order_by("hand_order"))
            n_sessions = 4

            for sn in range(1, n_sessions + 1):
                session_date = gd["start_date"] + timedelta(days=30 * (sn - 1))
                beneficiary = members[sn - 1] if sn <= len(members) else members[0]
                session = Session.objects.create(
                    group=group,
                    session_number=sn,
                    cycle=1,
                    date=session_date,
                    beneficiary=beneficiary,
                    status="completed",
                    opened_at=timezone.make_aware(
                        timezone.datetime.combine(session_date, timezone.datetime.min.time())
                    ),
                    closed_at=timezone.make_aware(
                        timezone.datetime.combine(session_date, timezone.datetime.min.time())
                        + timedelta(hours=3)
                    ),
                    created_by=members[0].user,
                )

                total = Decimal(0)
                for ms in members:
                    paid = random.random() > 0.1  # 90% taux de paiement
                    is_late = not paid and random.random() > 0.5
                    amount_paid = gd["contribution_amount"] if paid else 0
                    contrib = Contribution.objects.create(
                        membership=ms,
                        session=session,
                        amount_due=gd["contribution_amount"],
                        amount_paid=amount_paid,
                        status="paid" if paid else ("late" if is_late else "pending"),
                        payment_method=random.choice(["mtn_momo", "orange_money", "cash"]),
                        paid_at=timezone.make_aware(
                            timezone.datetime.combine(session_date, timezone.datetime.min.time())
                        ) if paid else None,
                        is_late=is_late,
                    )
                    if paid:
                        total += Decimal(amount_paid)
                        ms.total_contributed += Decimal(amount_paid)
                        ms.save(update_fields=["total_contributed"])

                session.total_collected = total
                session.hand_amount = total
                session.save(update_fields=["total_collected", "hand_amount"])

                beneficiary.total_received += total
                beneficiary.save(update_fields=["total_received"])

                # Transaction fond (pénalités fictives)
                FundTransaction.objects.create(
                    group=group,
                    type="hand_paid",
                    amount=total,
                    signed_amount=-total,
                    description=f"Main versée séance #{sn} — {beneficiary.user.get_full_name() or beneficiary.user.username}",
                    reference_session=session,
                    created_by=members[1].user,
                )

            self.stdout.write(f"   {n_sessions} séances créées pour '{group.name}'.")

            # ── 4. Dépôts fond commun ──────────────────────────────────────────
            depositors = members[:3]
            for ms in depositors:
                amount = Decimal(random.choice([50000, 100000, 150000]))
                dep = FundDeposit.objects.create(
                    membership=ms,
                    amount=amount,
                    duration_months=random.choice([3, 6]),
                    interest_rate=gd["fund_deposit_rate"],
                    status="active",
                )
                FundTransaction.objects.create(
                    group=group,
                    type="deposit_in",
                    amount=amount,
                    signed_amount=amount,
                    description=f"Dépôt fond commun — {ms.user.get_full_name() or ms.user.username}",
                    reference_deposit=dep,
                    created_by=ms.user,
                )

            # ── 5. Prêt actif ──────────────────────────────────────────────────
            borrower = members[4] if len(members) > 4 else members[-1]
            guarantor = members[2]
            loan_amount = Decimal(gd["contribution_amount"] * 2)
            duration = 3
            rate = Decimal(gd["fund_loan_rate"])
            total_interest = int(loan_amount * rate / 100 * duration)
            total_due = int(loan_amount) + total_interest

            loan = Loan.objects.create(
                membership=borrower,
                guarantor=guarantor,
                amount_requested=loan_amount,
                amount_approved=loan_amount,
                interest_rate=rate,
                duration_months=duration,
                purpose="Achat de matériel agricole pour la saison des pluies",
                status="active",
                approved_at=timezone.now() - timedelta(days=45),
                disbursed_at=timezone.now() - timedelta(days=45),
                due_date=(date.today() + timedelta(days=45)),
                total_interest=total_interest,
                total_due=total_due,
                total_repaid=0,
                reviewed_by=members[1].user,
            )
            FundTransaction.objects.create(
                group=group,
                type="loan_out",
                amount=loan_amount,
                signed_amount=-loan_amount,
                description=f"Prêt décaissé — {borrower.user.get_full_name() or borrower.user.username}",
                reference_loan=loan,
                created_by=members[1].user,
            )

            # Un remboursement partiel
            repaid = Decimal(total_due) / 3
            LoanRepayment.objects.create(
                loan=loan,
                amount_paid=repaid,
                principal_part=repaid * Decimal("0.7"),
                interest_part=repaid * Decimal("0.3"),
                balance_after=Decimal(total_due) - repaid,
                payment_method="mtn_momo",
                recorded_by=members[1].user,
            )
            loan.total_repaid = repaid
            loan.save(update_fields=["total_repaid"])

            # Notifications
            Notification.objects.create(
                membership=borrower,
                type="loan_approved",
                title="Prêt approuvé",
                body=f"Votre prêt de {int(loan_amount):,} FCFA a été approuvé et décaissé.",
                reference_loan=loan,
            )
            Notification.objects.create(
                membership=members[0],
                type="contribution_late",
                title="Cotisation en retard",
                body="2 membres n'ont pas encore payé leur cotisation pour la dernière séance.",
            )

        self.stdout.write(self.style.SUCCESS(
            "\nSeed Njangi+ termine avec succes !\n"
            "   -> Acces : /njangi/\n"
            "   -> Compte test : njangi_amara / njangi2026\n"
        ))
