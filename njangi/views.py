"""
Njangi+ — Vues
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView, CreateView, View
from django.http import HttpResponse
from django.utils import timezone

from .models import Group, Membership, Session, Contribution, FundDeposit, Loan, LoanRepayment, Notification, SubscriptionRequest
from .forms import GroupCreateForm, JoinGroupForm, LoanRequestForm, DepositCreateForm, ContributionPayForm, RepaymentForm


# ── Mixins ────────────────────────────────────────────────────────────────────

class MembershipRequiredMixin(LoginRequiredMixin):
    """Vérifie que l'utilisateur est membre du groupe passé en URL (slug)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        slug = kwargs.get("slug")
        if slug:
            self.group = get_object_or_404(Group, slug=slug)
            self.membership = get_object_or_404(Membership, group=self.group, user=request.user, is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if hasattr(self, "group"):
            ctx["group"] = self.group
            ctx["membership"] = self.membership
        return ctx


class BureauRequiredMixin(MembershipRequiredMixin):
    """Restreint aux membres du bureau (président, trésorier, secrétaire)."""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return response
        if hasattr(self, "membership") and not self.membership.is_bureau:
            messages.error(request, "Accès réservé au bureau du groupe.")
            return redirect("njangi:member_dashboard")
        return response


# ── Pages publiques ───────────────────────────────────────────────────────────

class LandingView(TemplateView):
    template_name = "njangi/landing.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx["memberships"] = Membership.objects.filter(
                user=self.request.user, is_active=True
            ).select_related("group")
        return ctx


class GroupDetailView(DetailView):
    model = Group
    template_name = "njangi/group_detail.html"
    context_object_name = "group"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        group = self.object
        ctx["members"] = group.memberships.filter(is_active=True).select_related("user")
        ctx["recent_sessions"] = group.sessions.order_by("-date")[:5]
        if self.request.user.is_authenticated:
            ctx["my_membership"] = Membership.objects.filter(
                group=group, user=self.request.user, is_active=True
            ).first()
        return ctx


class JoinGroupView(LoginRequiredMixin, View):
    template_name = "njangi/join.html"

    def get(self, request):
        from django.shortcuts import render
        return render(request, self.template_name, {"form": JoinGroupForm()})

    def post(self, request):
        from django.shortcuts import render
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["invite_code"].upper()
            group = get_object_or_404(Group, invite_code=code, status="active")

            # Vérifier si déjà membre
            existing = Membership.objects.filter(user=request.user, group=group).first()
            if existing:
                messages.info(request, "Vous êtes déjà membre de ce groupe.")
                return redirect("njangi:member_dashboard")

            # Vérifier la limite du plan
            if not group.can_add_member:
                messages.warning(
                    request,
                    f"Le groupe « {group.name} » a atteint la limite de son plan "
                    f"({group.plan_config['max_members']} membres). "
                    f"Le président doit passer à un plan supérieur."
                )
                return redirect("njangi:upgrade", slug=group.slug)

            Membership.objects.create(user=request.user, group=group, is_active=True)
            messages.success(request, f"Bienvenue dans le groupe « {group.name} » !")
            return redirect("njangi:member_dashboard")
        return render(request, self.template_name, {"form": form})


class CreateGroupView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupCreateForm
    template_name = "njangi/group_form.html"

    def form_valid(self, form):
        group = form.save(commit=False)
        group.created_by = self.request.user
        group.save()
        Membership.objects.create(
            user=self.request.user,
            group=group,
            role="president",
            hand_order=1,
            is_active=True,
        )
        messages.success(self.request, f"Groupe « {group.name} » créé avec succès !")
        return redirect("njangi:bureau_dashboard", slug=group.slug)


# ── Dashboard membre ──────────────────────────────────────────────────────────

class MemberDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "njangi/member/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        memberships = Membership.objects.filter(
            user=self.request.user, is_active=True
        ).select_related("group")
        ctx["memberships"] = memberships
        ctx["unread_count"] = Notification.objects.filter(
            membership__user=self.request.user, is_read=False
        ).count()
        return ctx


class MemberContributionsView(LoginRequiredMixin, TemplateView):
    template_name = "njangi/member/contributions.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        memberships = Membership.objects.filter(user=self.request.user, is_active=True)
        ctx["contributions"] = Contribution.objects.filter(
            membership__in=memberships
        ).select_related("session", "membership__group").order_by("-session__date")[:50]
        return ctx


class MemberLoansView(LoginRequiredMixin, TemplateView):
    template_name = "njangi/member/loans.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        memberships = Membership.objects.filter(user=self.request.user, is_active=True)
        ctx["loans"] = Loan.objects.filter(
            membership__in=memberships
        ).select_related("membership__group").order_by("-requested_at")
        return ctx


class LoanRequestView(LoginRequiredMixin, View):
    template_name = "njangi/member/loan_request.html"

    def get(self, request):
        from django.shortcuts import render
        return render(request, self.template_name, {
            "form": LoanRequestForm(user=request.user),
        })

    def post(self, request):
        from django.shortcuts import render
        form = LoanRequestForm(request.POST, user=request.user)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.interest_rate = loan.membership.group.fund_loan_rate
            loan.save()
            messages.success(request, "Votre demande de prêt a été soumise au bureau.")
            return redirect("njangi:member_loans")
        return render(request, self.template_name, {"form": form})


class MemberDepositsView(LoginRequiredMixin, TemplateView):
    template_name = "njangi/member/deposits.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        memberships = Membership.objects.filter(user=self.request.user, is_active=True)
        ctx["deposits"] = FundDeposit.objects.filter(
            membership__in=memberships
        ).select_related("membership__group").order_by("-deposited_at")
        return ctx


class DepositCreateView(LoginRequiredMixin, View):
    template_name = "njangi/member/deposit_form.html"

    def get(self, request):
        from django.shortcuts import render
        return render(request, self.template_name, {
            "form": DepositCreateForm(user=request.user)
        })

    def post(self, request):
        from django.shortcuts import render
        form = DepositCreateForm(request.POST, user=request.user)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.interest_rate = deposit.membership.group.fund_deposit_rate
            deposit.save()
            from .models import FundTransaction
            FundTransaction.objects.create(
                group=deposit.membership.group,
                type="deposit_in",
                amount=deposit.amount,
                description=f"Dépôt fond commun — {request.user}",
                reference_deposit=deposit,
                created_by=request.user,
            )
            messages.success(request, "Dépôt enregistré avec succès !")
            return redirect("njangi:member_deposits")
        return render(request, self.template_name, {"form": form})


class DepositWithdrawView(LoginRequiredMixin, View):
    def post(self, request, pk):
        deposit = get_object_or_404(FundDeposit, pk=pk, membership__user=request.user, status="active")
        deposit.withdraw(user=request.user)
        messages.success(
            request,
            f"Retrait effectué : {int(deposit.withdrawn_amount):,} FCFA "
            f"(dont {int(deposit.interest_earned):,} FCFA d'intérêts)."
        )
        return redirect("njangi:member_deposits")


class MemberNotificationsView(LoginRequiredMixin, TemplateView):
    template_name = "njangi/member/notifications.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        memberships = Membership.objects.filter(user=self.request.user, is_active=True)
        notifications = Notification.objects.filter(
            membership__in=memberships
        ).select_related("membership__group").order_by("-created_at")[:60]
        Notification.objects.filter(
            membership__in=memberships, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        ctx["notifications"] = notifications
        return ctx


# ── Bureau ────────────────────────────────────────────────────────────────────

class BureauDashboardView(BureauRequiredMixin, TemplateView):
    template_name = "njangi/bureau/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        group = self.group
        ctx["pending_loans_count"] = Loan.objects.filter(membership__group=group, status="pending").count()
        ctx["active_loans"] = Loan.objects.filter(membership__group=group, status="active")
        ctx["next_session"] = group.sessions.filter(status__in=("planned", "in_progress")).first()
        ctx["recent_transactions"] = group.fund_transactions.order_by("-created_at")[:10]
        return ctx


class BureauMembersView(BureauRequiredMixin, TemplateView):
    template_name = "njangi/bureau/members.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["members"] = self.group.memberships.filter(is_active=True).select_related("user")
        return ctx


class BureauSessionsView(BureauRequiredMixin, TemplateView):
    template_name = "njangi/bureau/sessions.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["sessions"] = self.group.sessions.order_by("-date")[:30]
        return ctx


class SessionCreateView(BureauRequiredMixin, View):
    template_name = "njangi/bureau/session_form.html"

    def get(self, request, slug):
        from django.shortcuts import render
        from .forms import SessionCreateForm
        return render(request, self.template_name, {
            "form": SessionCreateForm(group=self.group),
            "group": self.group,
            "membership": self.membership,
        })

    def post(self, request, slug):
        from django.shortcuts import render
        from .forms import SessionCreateForm
        form = SessionCreateForm(request.POST, group=self.group)
        if form.is_valid():
            session = form.save(commit=False)
            session.group = self.group
            session.cycle = self.group.current_cycle
            session.created_by = request.user
            session.save()
            members = self.group.memberships.filter(is_active=True)
            Contribution.objects.bulk_create([
                Contribution(
                    membership=m,
                    session=session,
                    amount_due=self.group.contribution_amount,
                )
                for m in members
            ])
            messages.success(request, f"Séance #{session.session_number} créée avec {members.count()} cotisations.")
            return redirect("njangi:session_detail", slug=slug, pk=session.pk)
        return render(request, self.template_name, {"form": form, "group": self.group, "membership": self.membership})


class SessionDetailView(BureauRequiredMixin, TemplateView):
    template_name = "njangi/bureau/session_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        session = get_object_or_404(Session, pk=self.kwargs["pk"], group=self.group)
        ctx["session"] = session
        ctx["contributions"] = session.contributions.select_related("membership__user").order_by("membership__hand_order")
        ctx["pay_form"] = ContributionPayForm()
        return ctx


class SessionOpenView(BureauRequiredMixin, View):
    def post(self, request, slug, pk):
        session = get_object_or_404(Session, pk=pk, group=self.group, status="planned")
        session.open(user=request.user)
        messages.success(request, f"Séance #{session.session_number} ouverte.")
        return redirect("njangi:session_detail", slug=slug, pk=pk)


class SessionCloseView(BureauRequiredMixin, View):
    def post(self, request, slug, pk):
        session = get_object_or_404(Session, pk=pk, group=self.group, status="in_progress")
        session.close(user=request.user)
        messages.success(request, f"Séance #{session.session_number} clôturée. Total : {session.formatted_hand}.")
        return redirect("njangi:session_detail", slug=slug, pk=pk)


class BureauLoansView(BureauRequiredMixin, TemplateView):
    template_name = "njangi/bureau/loans.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["pending_loans"] = Loan.objects.filter(membership__group=self.group, status="pending").select_related("membership__user")
        ctx["active_loans"]  = Loan.objects.filter(membership__group=self.group, status="active").select_related("membership__user")
        ctx["closed_loans"]  = Loan.objects.filter(membership__group=self.group, status__in=("completed", "rejected")).select_related("membership__user")[:20]
        ctx["repayment_form"] = RepaymentForm()
        return ctx


class LoanApproveView(BureauRequiredMixin, View):
    def post(self, request, slug, pk):
        loan = get_object_or_404(Loan, pk=pk, membership__group=self.group, status="pending")
        loan.approve(reviewer=request.user)
        messages.success(request, f"Prêt de {loan.formatted_amount} approuvé.")
        return redirect("njangi:bureau_loans", slug=slug)


class LoanRejectView(BureauRequiredMixin, View):
    def post(self, request, slug, pk):
        loan = get_object_or_404(Loan, pk=pk, membership__group=self.group, status="pending")
        reason = request.POST.get("reason", "")
        loan.reject(reviewer=request.user, reason=reason)
        messages.warning(request, "Demande de prêt refusée.")
        return redirect("njangi:bureau_loans", slug=slug)


class LoanDisburseView(BureauRequiredMixin, View):
    def post(self, request, slug, pk):
        loan = get_object_or_404(Loan, pk=pk, membership__group=self.group, status="approved")
        loan.disburse(user=request.user)
        messages.success(request, f"Prêt décaissé : {loan.formatted_amount} versés.")
        return redirect("njangi:bureau_loans", slug=slug)


class FundView(BureauRequiredMixin, TemplateView):
    template_name = "njangi/bureau/fund.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        group = self.group
        ctx["transactions"] = group.fund_transactions.order_by("-created_at")[:50]
        ctx["deposits"] = FundDeposit.objects.filter(
            membership__group=group, status="active"
        ).select_related("membership__user")
        ctx["balance"] = group.fund_balance
        ctx["available"] = group.fund_available_for_loans
        return ctx


# ── HTMX partials ─────────────────────────────────────────────────────────────

class HtmxContributionPayView(LoginRequiredMixin, View):
    def post(self, request, pk):
        contribution = get_object_or_404(Contribution, pk=pk, membership__user=request.user)
        form = ContributionPayForm(request.POST)
        if form.is_valid():
            contribution.mark_paid(
                amount=form.cleaned_data["amount"],
                method=form.cleaned_data["payment_method"],
                ref=form.cleaned_data.get("transaction_ref", ""),
                user=request.user,
            )
        from django.template.loader import render_to_string
        html = render_to_string(
            "njangi/partials/contribution_row.html",
            {"contribution": contribution},
            request=request,
        )
        return HttpResponse(html)


class HtmxRepaymentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        loan = get_object_or_404(Loan, pk=pk, membership__user=request.user, status="active")
        form = RepaymentForm(request.POST)
        if form.is_valid():
            LoanRepayment.objects.create(
                loan=loan,
                amount_paid=form.cleaned_data["amount"],
                payment_method=form.cleaned_data["payment_method"],
                transaction_ref=form.cleaned_data.get("transaction_ref", ""),
                recorded_by=request.user,
            )
            messages.success(request, "Remboursement enregistré.")
        return redirect("njangi:member_loans")


class HtmxMarkNotificationsRead(LoginRequiredMixin, View):
    def post(self, request):
        memberships = Membership.objects.filter(user=request.user, is_active=True)
        Notification.objects.filter(
            membership__in=memberships, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return HttpResponse("")


class PremiumView(TemplateView):
    """Page des plans premium Njangi — chargée depuis l'admin PlanPremiumApp."""
    template_name = "njangi/premium.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            from payments.models import PlanPremiumApp
            plans = list(PlanPremiumApp.objects.filter(module='njangi', actif=True).order_by('ordre', 'prix'))
        except Exception:
            plans = []
        ctx['plans'] = plans
        return ctx


# ── Wallet / Intérêts membres ─────────────────────────────────────────────────

class MemberWalletView(LoginRequiredMixin, TemplateView):
    """Portfolio personnel : dépôts + intérêts cumulés + évolution Chart.js."""
    template_name = "njangi/member/wallet.html"

    def get_context_data(self, **kwargs):
        from njangi.services import InterestCalculationService
        ctx = super().get_context_data(**kwargs)
        memberships = Membership.objects.filter(
            user=self.request.user, is_active=True
        ).select_related("group")

        wallet_data = []
        for ms in memberships:
            evolution = InterestCalculationService.get_member_evolution(ms, last_n_months=12)
            deposits = FundDeposit.objects.filter(
                membership=ms, status="active"
            ).order_by("-deposited_at")
            wallet_data.append({
                "membership": ms,
                "deposits": deposits,
                "evolution": evolution,          # list of dicts: {label, interest, wallet_balance}
                "wallet_balance": ms.wallet_balance,
                "total_interest_earned": ms.total_interest_earned,
                "active_deposit_balance": ms.active_deposit_balance,
                "base_fund_deficit": ms.base_fund_deficit,
            })

        ctx["wallet_data"] = wallet_data
        return ctx


# ── Bureau — Intérêts mensuels ────────────────────────────────────────────────

class BureauMonthlyInterestView(BureauRequiredMixin, TemplateView):
    """Liste des relevés mensuels d'intérêts pour le groupe."""
    template_name = "njangi/bureau/monthly_interest.html"

    def get_context_data(self, **kwargs):
        from njangi.models.wallet import MonthlyGroupInterest
        from njangi.services import InterestCalculationService
        ctx = super().get_context_data(**kwargs)
        group = self.group

        ctx["records"] = MonthlyGroupInterest.objects.filter(
            group=group
        ).prefetch_related("member_statements__membership__user").order_by("-year", "-month")

        # Projection mois suivant
        try:
            ctx["projection"] = InterestCalculationService.simulate_next_month(group)
        except Exception:
            ctx["projection"] = None

        return ctx


class BureauCalculateInterestView(BureauRequiredMixin, View):
    """Déclenche le calcul des intérêts pour un mois donné (POST)."""

    def post(self, request, slug):
        from njangi.services import InterestCalculationService
        import json

        year  = int(request.POST.get("year",  timezone.now().year))
        month = int(request.POST.get("month", timezone.now().month))

        try:
            record = InterestCalculationService.calculate_month(self.group, year, month)
            messages.success(
                request,
                f"Intérêts {month:02d}/{year} calculés : "
                f"{int(record.total_interest_generated):,} FCFA répartis entre "
                f"{record.nb_depositors} déposant(s)."
            )
        except Exception as exc:
            messages.error(request, f"Erreur lors du calcul : {exc}")

        return redirect("njangi:bureau_monthly_interest", slug=slug)


# ── Bureau — Distribution (bouffe / main) ─────────────────────────────────────

class DistributionPreviewView(BureauRequiredMixin, View):
    """Aperçu des déductions avant distribution de la main à un membre."""
    template_name = "njangi/bureau/distribution_preview.html"

    def get(self, request, slug, membership_pk):
        from django.shortcuts import render
        from njangi.services import DistributionCalculator

        member_ms = get_object_or_404(
            Membership, pk=membership_pk, group=self.group, is_active=True
        )
        gross = self.group.contribution_amount * self.group.member_count
        preview = DistributionCalculator.preview(member_ms, gross_amount=gross)

        return render(request, self.template_name, {
            "group": self.group,
            "membership": self.membership,
            "recipient": member_ms,
            "preview": preview,
        })

    def post(self, request, slug, membership_pk):
        """Confirme et enregistre la distribution."""
        from njangi.services import DistributionCalculator
        from njangi.models import Session

        member_ms = get_object_or_404(
            Membership, pk=membership_pk, group=self.group, is_active=True
        )
        gross = self.group.contribution_amount * self.group.member_count
        preview = DistributionCalculator.preview(member_ms, gross_amount=gross)

        if not preview["can_receive"]:
            messages.error(
                request,
                f"Distribution bloquée : {preview.get('blocked', 'conditions non remplies')}."
            )
            return redirect("njangi:bureau_members", slug=slug)

        # Enregistrement dans la session en cours (si existante)
        active_session = self.group.sessions.filter(status="in_progress").first()
        if active_session:
            active_session.beneficiary  = member_ms
            active_session.hand_amount  = preview["net_amount"]
            active_session.save(update_fields=["beneficiary", "hand_amount"])
            member_ms.total_received += preview["net_amount"]
            member_ms.save(update_fields=["total_received"])
            messages.success(
                request,
                f"Distribution confirmée : {int(preview['net_amount']):,} FCFA versés à {member_ms.user}."
            )
        else:
            messages.warning(request, "Aucune séance en cours — distribution non enregistrée.")

        return redirect("njangi:bureau_members", slug=slug)


# ── Abonnement / Upgrade ──────────────────────────────────────────────────────

class UpgradeView(MembershipRequiredMixin, TemplateView):
    """Page d'upgrade — affiche les plans et les instructions de paiement."""
    template_name = "njangi/upgrade.html"

    def get_context_data(self, **kwargs):
        from njangi.models.group import PLAN_CONFIG
        ctx = super().get_context_data(**kwargs)
        ctx["plan_config"] = PLAN_CONFIG
        ctx["pending_request"] = SubscriptionRequest.objects.filter(
            group=self.group, status="pending"
        ).first()
        return ctx


class SubscriptionRequestView(MembershipRequiredMixin, View):
    """Soumettre une demande d'abonnement après paiement."""
    template_name = "njangi/subscription_request.html"

    def get(self, request, slug):
        from django.shortcuts import render
        from njangi.models.group import PLAN_CONFIG
        plan = request.GET.get("plan", "standard")
        duration = int(request.GET.get("duration", 1))
        return render(request, self.template_name, {
            "group": self.group,
            "membership": self.membership,
            "plan": plan,
            "duration": duration,
            "plan_config": PLAN_CONFIG,
        })

    def post(self, request, slug):
        plan = request.POST.get("plan", "standard")
        duration = int(request.POST.get("duration_months", 1))
        sub = SubscriptionRequest(
            group=self.group,
            requested_by=request.user,
            plan=plan,
            duration_months=duration,
            payment_method=request.POST.get("payment_method", "mtn_momo"),
            phone_used=request.POST.get("phone_used", ""),
            payment_date=request.POST.get("payment_date"),
            payment_ref=request.POST.get("payment_ref", ""),
            amount_paid=request.POST.get("amount_paid", 0),
            notes=request.POST.get("notes", ""),
        )
        sub.compute_amount()
        sub.save()
        messages.success(
            request,
            "Demande enregistrée ! Le fondateur va vérifier votre paiement "
            "et activer votre groupe sous 24h. Merci !"
        )
        return redirect("njangi:upgrade", slug=slug)
