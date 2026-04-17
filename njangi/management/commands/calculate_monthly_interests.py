"""
Commande Django : Calcul des intérêts mensuels Njangi+

Usage :
  # Mois en cours pour tous les groupes
  python manage.py calculate_monthly_interests

  # Mois spécifique, tous groupes
  python manage.py calculate_monthly_interests --year 2026 --month 3

  # Groupe spécifique
  python manage.py calculate_monthly_interests --group mon-groupe

  # Recalculer tous les mois depuis la création du groupe
  python manage.py calculate_monthly_interests --group mon-groupe --all-months

  # Mode simulation (pas de sauvegarde)
  python manage.py calculate_monthly_interests --dry-run

  # Voir la projection du mois prochain
  python manage.py calculate_monthly_interests --group mon-groupe --simulate
"""
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = "Calcule les intérêts mensuels proportionnels pour les groupes Njangi+"

    def add_arguments(self, parser):
        parser.add_argument(
            "--group",
            type=str,
            default=None,
            metavar="SLUG",
            help="Slug du groupe (défaut : tous les groupes actifs)",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=None,
            help="Année (défaut : année courante)",
        )
        parser.add_argument(
            "--month",
            type=int,
            default=None,
            help="Mois 1-12 (défaut : mois courant)",
        )
        parser.add_argument(
            "--all-months",
            action="store_true",
            help="Recalculer tous les mois depuis la création du groupe",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulation : affiche les résultats sans sauvegarder",
        )
        parser.add_argument(
            "--simulate",
            action="store_true",
            help="Affiche la projection du mois prochain sans sauvegarder",
        )

    def handle(self, *args, **options):
        from njangi.models import Group
        from njangi.services import InterestCalculationService

        today = timezone.now().date()
        year  = options["year"]  or today.year
        month = options["month"] or today.month

        if not 1 <= month <= 12:
            raise CommandError(f"Mois invalide : {month}. Doit être entre 1 et 12.")

        # ── Sélection des groupes ─────────────────────────────────────────────
        if options["group"]:
            try:
                groups = [Group.objects.get(slug=options["group"])]
            except Group.DoesNotExist:
                raise CommandError(f"Groupe introuvable : '{options['group']}'")
        else:
            groups = list(Group.objects.filter(status="active"))

        if not groups:
            self.stdout.write(self.style.WARNING("Aucun groupe actif trouvé."))
            return

        self.stdout.write(
            self.style.HTTP_INFO(
                f"\n{'='*60}\n"
                f"  Calcul intérêts Njangi+\n"
                f"  {len(groups)} groupe(s) | Mois cible : {month:02d}/{year}\n"
                f"{'='*60}\n"
            )
        )

        # ── Mode simulation (projection mois prochain) ────────────────────────
        if options["simulate"]:
            for group in groups:
                self._simulate_next_month(group, InterestCalculationService)
            return

        # ── Calcul réel ───────────────────────────────────────────────────────
        total_groups   = 0
        total_interest = 0

        for group in groups:
            if options["all_months"]:
                results = self._calculate_all_months(
                    group, InterestCalculationService, dry_run=options["dry_run"]
                )
                total_interest += sum(r.get("interest", 0) for r in results)
                total_groups += 1
            else:
                result = self._calculate_one_month(
                    group, year, month, InterestCalculationService,
                    dry_run=options["dry_run"]
                )
                if result:
                    total_interest += result
                    total_groups += 1

        # ── Résumé final ─────────────────────────────────────────────────────
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'='*60}\n"
                f"  Terminé : {total_groups} groupe(s) traité(s)\n"
                f"  Intérêts totaux générés : {int(total_interest):,} FCFA\n"
                f"{'='*60}\n"
            )
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _calculate_one_month(self, group, year, month, service, dry_run=False):
        """Calcule les intérêts d'un groupe pour un mois donné."""
        self.stdout.write(
            f"\n  Groupe : {self.style.MIGRATE_HEADING(group.name)}"
            f"  ({month:02d}/{year})"
        )

        if dry_run:
            # Aperçu sans sauvegarde
            preview = self._dry_run_preview(group, year, month, service)
            self._print_month_preview(preview)
            return preview.get("total_interest", 0)

        try:
            record = service.calculate_month(group, year, month)
        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"    ✗ Erreur : {exc}")
            )
            return 0

        interest = int(record.total_interest_generated)
        pool     = int(record.total_pool)
        nb_loans = record.nb_active_loans
        nb_dep   = record.nb_depositors

        self.stdout.write(
            f"    ✓ Pool : {pool:>12,} FCFA | "
            f"Prêts actifs : {nb_loans} | "
            f"Déposants : {nb_dep} | "
            f"Intérêts : {interest:>10,} FCFA"
        )

        # Détail par membre
        if nb_dep:
            self.stdout.write("    ┌─ Détail membres ─────────────────────────────────────")
            for stmt in record.member_statements.select_related("membership__user").order_by("-deposit_balance"):
                self.stdout.write(
                    f"    │  {stmt.membership.user:<20} "
                    f"Dépôt {int(stmt.deposit_balance):>10,} FCFA  "
                    f"Part {float(stmt.pool_share_pct):>5.1f}%  "
                    f"+{int(stmt.interest_earned):>8,} FCFA"
                )
            self.stdout.write("    └──────────────────────────────────────────────────────")

        return interest

    def _calculate_all_months(self, group, service, dry_run=False):
        """Recalcule tous les mois depuis start_date du groupe jusqu'au mois courant."""
        from njangi.services import _first_day
        today = timezone.now().date()
        start = group.start_date

        self.stdout.write(
            f"\n  Groupe : {self.style.MIGRATE_HEADING(group.name)}"
            f"  — recalcul depuis {start.strftime('%m/%Y')}"
        )

        results = []
        year, month = start.year, start.month

        while (year, month) <= (today.year, today.month):
            if dry_run:
                preview = self._dry_run_preview(group, year, month, service)
                results.append({"year": year, "month": month, "interest": preview.get("total_interest", 0)})
                self.stdout.write(
                    f"    [DRY-RUN] {month:02d}/{year} — "
                    f"Intérêts estimés : {int(preview.get('total_interest', 0)):,} FCFA"
                )
            else:
                try:
                    record = service.calculate_month(group, year, month)
                    interest = int(record.total_interest_generated)
                    results.append({"year": year, "month": month, "interest": interest})
                    self.stdout.write(
                        f"    ✓ {month:02d}/{year} — "
                        f"Pool : {int(record.total_pool):,} FCFA | "
                        f"Intérêts : {interest:,} FCFA | "
                        f"Prêts actifs : {record.nb_active_loans}"
                    )
                except Exception as exc:
                    self.stderr.write(
                        self.style.ERROR(f"    ✗ {month:02d}/{year} — Erreur : {exc}")
                    )
                    results.append({"year": year, "month": month, "interest": 0})

            # Passer au mois suivant
            if month == 12:
                year, month = year + 1, 1
            else:
                month += 1

        return results

    def _simulate_next_month(self, group, service):
        """Affiche la projection du mois prochain."""
        self.stdout.write(
            f"\n  Groupe : {self.style.MIGRATE_HEADING(group.name)} — Projection mois prochain"
        )
        try:
            proj = service.simulate_next_month(group)
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"    ✗ Erreur simulation : {exc}"))
            return

        self.stdout.write(
            f"    Pool estimé           : {int(proj['pool_total']):>12,} FCFA\n"
            f"    Encours prêts         : {int(proj['loans_outstanding']):>12,} FCFA\n"
            f"    Taux utilisation      : {proj['utilization_rate']:>11.1f} %\n"
            f"    Intérêts projetés     : {int(proj['projected_interest']):>12,} FCFA\n"
            f"    Déposants             : {proj['nb_depositors']:>12}\n"
            f"    Prêts actifs          : {proj['nb_active_loans']:>12}"
        )

        if proj.get("member_projections"):
            self.stdout.write("    ┌─ Projection par membre ──────────────────────────────")
            for mp in proj["member_projections"]:
                self.stdout.write(
                    f"    │  {mp['user']:<20} "
                    f"Dépôt {int(mp['deposit']):>10,} FCFA  "
                    f"Part {mp['share_pct']:>5.1f}%  "
                    f"+{int(mp['projected_interest']):>8,} FCFA"
                )
            self.stdout.write("    └──────────────────────────────────────────────────────")

    def _dry_run_preview(self, group, year, month, service):
        """Calcule en mémoire sans sauvegarder (pour dry-run)."""
        from calendar import monthrange
        from datetime import date
        from njangi.models import Membership
        from njangi.models.fund import FundDeposit, FundTransaction
        from njangi.models.loan import Loan
        from django.db.models import Sum, Q

        first_day = date(year, month, 1)
        last_day  = date(year, month, monthrange(year, month)[1])

        deposits = FundDeposit.objects.filter(
            membership__group=group,
            status="active",
            deposited_at__date__lte=last_day,
        ).filter(Q(withdrawn_at__isnull=True) | Q(withdrawn_at__date__gt=first_day))

        pool_total = deposits.aggregate(t=Sum("amount"))["t"] or 0

        loans = Loan.objects.filter(
            membership__group=group,
            status__in=("active", "completed"),
            disbursed_at__date__lte=last_day,
        ).filter(Q(completed_at__isnull=True) | Q(completed_at__date__gt=first_day))

        total_interest = sum(
            float(loan.amount_approved) * float(loan.interest_rate) / 100
            for loan in loans
        )

        return {
            "pool_total": float(pool_total),
            "total_interest": total_interest,
            "nb_depositors": deposits.values("membership").distinct().count(),
            "nb_active_loans": loans.count(),
        }

    def _print_month_preview(self, preview):
        self.stdout.write(
            f"    [DRY-RUN] Pool : {int(preview['pool_total']):,} FCFA | "
            f"Intérêts estimés : {int(preview['total_interest']):,} FCFA | "
            f"Déposants : {preview['nb_depositors']} | "
            f"Prêts : {preview['nb_active_loans']}"
        )
