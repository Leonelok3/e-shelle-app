"""
Njangi+ — Tâches Celery asynchrones

Planification automatique :
  - 1er du mois à 2h    → calcul intérêts mensuels
  - Chaque jour à 6h    → application des pénalités de retard
  - Chaque jour à 7h    → vérification des défauts de prêts
  - Chaque dimanche 3h  → mise à jour scores de fiabilité
"""
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(
    name="njangi.tasks.calculate_monthly_interests_all",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def calculate_monthly_interests_all(self):
    """
    Calcule les intérêts mensuels pour tous les groupes actifs.
    Déclenché le 1er de chaque mois à 2h00.
    """
    from datetime import date
    from njangi.models import Group
    from njangi.services import InterestCalculationService

    today = date.today()
    groups = Group.objects.filter(status="active")
    results = []

    for group in groups:
        try:
            record = InterestCalculationService.calculate_month(group, today.year, today.month)
            msg = f"{group.name}: {record.formatted_interest} générés ({record.nb_depositors} déposants)"
            results.append(msg)
            logger.info(f"[Njangi] {msg}")
        except Exception as exc:
            logger.error(f"[Njangi] Erreur calcul intérêts {group.name}: {exc}", exc_info=True)
            try:
                self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                logger.critical(f"[Njangi] Échec définitif calcul intérêts {group.name}")

    logger.info(f"[Njangi] Calcul mensuel terminé — {len(results)} groupes traités")
    return results


@shared_task(
    name="njangi.tasks.apply_penalties_all",
    bind=True,
    max_retries=2,
    default_retry_delay=120,
)
def apply_penalties_all(self):
    """
    Applique les pénalités de retard sur toutes les cotisations impayées.
    Déclenché chaque jour à 6h00.
    """
    from njangi.models import Group
    from njangi.services import PenaltyService

    groups = Group.objects.filter(status="active")
    total_penalties = 0
    affected_groups = 0

    for group in groups:
        try:
            penalties = PenaltyService.apply_all_pending(group) or 0
            if penalties > 0:
                total_penalties += penalties
                affected_groups += 1
                logger.info(f"[Njangi] Pénalités {group.name}: {penalties:,} FCFA")
        except Exception as exc:
            logger.error(f"[Njangi] Erreur pénalités {group.name}: {exc}", exc_info=True)

    logger.info(f"[Njangi] Pénalités appliquées — {affected_groups} groupes — total: {total_penalties:,} FCFA")
    return {"total_fcfa": total_penalties, "groups_affected": affected_groups}


@shared_task(
    name="njangi.tasks.check_loan_defaults",
    bind=True,
)
def check_loan_defaults(self):
    """
    Marque en défaut tous les prêts actifs échus non remboursés.
    Déclenché chaque jour à 7h00.
    """
    from njangi.models.loan import Loan

    active_loans = Loan.objects.filter(status="active").select_related("membership__group")
    defaulted = 0

    for loan in active_loans:
        if loan.is_overdue:
            loan.mark_defaulted()
            defaulted += 1
            logger.warning(
                f"[Njangi] Prêt en défaut: {loan.membership.user} "
                f"({loan.membership.group.name}) — {loan.formatted_amount}"
            )

    logger.info(f"[Njangi] Défauts vérifiés — {defaulted} prêt(s) marqué(s) en défaut")
    return defaulted


@shared_task(
    name="njangi.tasks.update_reliability_scores",
)
def update_reliability_scores():
    """
    Recalcule les scores de fiabilité de tous les membres actifs.
    Déclenché chaque dimanche à 3h00.
    """
    from njangi.models import Group
    from njangi.services import ReliabilityScoreService

    groups = Group.objects.filter(status="active")
    updated = 0

    for group in groups:
        try:
            members = group.memberships.filter(is_active=True)
            for membership in members:
                ReliabilityScoreService.update(membership)
                updated += 1
        except Exception as exc:
            logger.error(f"[Njangi] Erreur scores fiabilité {group.name}: {exc}", exc_info=True)

    logger.info(f"[Njangi] Scores fiabilité mis à jour — {updated} membres")
    return updated


@shared_task(
    name="njangi.tasks.calculate_monthly_interests_group",
)
def calculate_monthly_interests_group(group_id, year, month):
    """
    Calcule les intérêts mensuels pour UN groupe spécifique.
    Peut être déclenché manuellement depuis l'interface bureau.
    """
    from njangi.models import Group
    from njangi.services import InterestCalculationService

    try:
        group = Group.objects.get(pk=group_id)
        record = InterestCalculationService.calculate_month(group, year, month)
        logger.info(f"[Njangi] Intérêts calculés (manuel) — {group.name} {month:02d}/{year}: {record.formatted_interest}")
        return {
            "group": group.name,
            "year": year,
            "month": month,
            "interest": int(record.total_interest_generated),
            "depositors": record.nb_depositors,
        }
    except Group.DoesNotExist:
        logger.error(f"[Njangi] Groupe introuvable: pk={group_id}")
        return None
    except Exception as exc:
        logger.error(f"[Njangi] Erreur calcul intérêts groupe {group_id}: {exc}", exc_info=True)
        raise
